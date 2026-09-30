from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def override_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)
USER = {"email": "a@example.com", "password": "supersecret1", "full_name": "Alice"}


def login(password="supersecret1"):
    return client.post("/api/v1/auth/login", data={"username": USER["email"], "password": password})


def test_full_flow():
    assert client.post("/api/v1/auth/register", json=USER).status_code == 201
    assert client.post("/api/v1/auth/register", json=USER).status_code == 409
    assert login("wrong-password").status_code == 401

    tokens = login().json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    assert client.get("/api/v1/users/me", headers=headers).json()["email"] == USER["email"]

    # refresh token must not work as an access token, and vice versa
    bad = {"Authorization": f"Bearer {tokens['refresh_token']}"}
    assert client.get("/api/v1/users/me", headers=bad).status_code == 401
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["access_token"]}).status_code == 401
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 200

    # normal users can't list users; no token = 401
    assert client.get("/api/v1/users/", headers=headers).status_code == 403
    assert client.get("/api/v1/users/me").status_code == 401
