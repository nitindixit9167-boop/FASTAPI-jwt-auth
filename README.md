# FastAPI JWT Auth

A small, production-minded FastAPI service showing **OAuth2 password flow + JWT**
(access and refresh tokens), bcrypt password hashing, role-based access and tests.

## Features
- Register / login / refresh endpoints under `/api/v1/auth`
- OAuth2 password flow, so the **Authorize** button in Swagger UI (`/docs`) works
- Short-lived access token (15 min) and long-lived refresh token (7 days)
- Token `type` claim, so a refresh token can't be used as an access token
- bcrypt password hashing, SQLAlchemy 2.0 models, Pydantic v2 schemas
- Role-based access (`user` / `admin`) via dependencies
- Config from environment / `.env`, Dockerfile, pytest suite

## Project layout
```
app/
  main.py          app factory, routers, startup
  db.py            engine, session, get_db
  models.py        User table
  schemas.py       request/response models
  deps.py          get_current_user, require_admin
  core/config.py   settings
  core/security.py hashing + JWT create/decode
  routers/auth.py  register, login, refresh
  routers/users.py /me, admin user list
tests/test_auth.py end-to-end auth test
```

## Run it
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then set a real SECRET_KEY
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs

## Try it
```bash
curl -X POST localhost:8000/api/v1/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"me@example.com","password":"supersecret1"}'

curl -X POST localhost:8000/api/v1/auth/login \
  -d 'username=me@example.com&password=supersecret1'

curl localhost:8000/api/v1/users/me -H "Authorization: Bearer <access_token>"
```

## Tests / Docker
```bash
pytest
docker build -t fastapi-jwt . && docker run -p 8000:8000 --env-file .env fastapi-jwt
```

## Make a user admin
```bash
sqlite3 app.db "UPDATE users SET role='admin' WHERE email='me@example.com';"
```

## Before production
- Use a strong random `SECRET_KEY` and HTTPS
- Replace `create_all` with Alembic migrations and SQLite with Postgres
- Add refresh-token rotation/revocation (store `jti`), rate limiting on login, CORS config
