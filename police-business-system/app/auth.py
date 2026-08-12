"""簡單的自建帳號密碼登入（8 人規模不需要接 AD/LDAP），
用 itsdangerous 簽章的 cookie 保存 session，僅限內網使用。"""

import os

from fastapi import Cookie, Depends, HTTPException, status
from itsdangerous import BadSignature, URLSafeTimedSerializer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
SESSION_COOKIE = "session"
SESSION_MAX_AGE = 60 * 60 * 12  # 12 小時

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeTimedSerializer(SECRET_KEY)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_session_token(user_id: int) -> str:
    return serializer.dumps({"user_id": user_id})


def get_current_user(
    session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    db: Session = Depends(get_db),
) -> User:
    if session is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "請先登入")
    try:
        data = serializer.loads(session, max_age=SESSION_MAX_AGE)
    except BadSignature:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "登入已過期，請重新登入")

    user = db.get(User, data["user_id"])
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "帳號不存在")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "僅限管理者操作")
    return user
