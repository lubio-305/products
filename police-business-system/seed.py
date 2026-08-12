"""初次部署用：建立第一個管理者帳號。
用法： python seed.py <帳號> <密碼> <顯示名稱>"""

import sys

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import User
from app.services.colors import next_color

Base.metadata.create_all(bind=engine)


def main():
    if len(sys.argv) != 4:
        print("用法: python seed.py <帳號> <密碼> <顯示名稱>")
        sys.exit(1)

    username, password, display_name = sys.argv[1:4]
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == username).first():
            print(f"帳號 {username} 已存在")
            return
        db.add(
            User(
                username=username,
                password_hash=hash_password(password),
                display_name=display_name,
                is_admin=True,
                color=next_color(db),
            )
        )
        db.commit()
        print(f"已建立管理者帳號：{username}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
