import os
import shutil
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="pbs_test_")
os.environ["DISABLE_SCHEDULER"] = "1"

import pytest
from fastapi.testclient import TestClient

from app.auth import hash_password
from app.database import UPLOAD_DIR, Base, SessionLocal, engine
from app.main import app
from app.models import User
from app.services.colors import next_color


@pytest.fixture(autouse=True)
def _reset_state():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    for name in os.listdir(UPLOAD_DIR):
        path = os.path.join(UPLOAD_DIR, name)
        shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)

    yield


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    return TestClient(app)


def make_user(db, username, password, display_name, is_admin=False):
    user = User(
        username=username,
        password_hash=hash_password(password),
        display_name=display_name,
        is_admin=is_admin,
        color=next_color(db),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    return make_user(db_session, "admin", "adminpass", "管理者", is_admin=True)


@pytest.fixture
def staff_user(db_session):
    return make_user(db_session, "chen", "chenpass", "陳小明", is_admin=False)


@pytest.fixture
def other_staff_user(db_session):
    return make_user(db_session, "wang", "wangpass", "王小華", is_admin=False)


@pytest.fixture
def admin_client(admin_user):
    # 用獨立的 TestClient（獨立 cookie jar），才不會跟 staff_client 共用同一個
    # session cookie、互相把對方登出。
    c = TestClient(app)
    resp = c.post("/api/auth/login", json={"username": "admin", "password": "adminpass"})
    assert resp.status_code == 200
    return c


@pytest.fixture
def staff_client(staff_user):
    c = TestClient(app)
    resp = c.post("/api/auth/login", json={"username": "chen", "password": "chenpass"})
    assert resp.status_code == 200
    return c
