from datetime import datetime, timedelta, timezone
from typing import Annotated

import secrets
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

SECRET_KEY = "change-me-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


class AuthData(BaseModel):
    username: str
    password: str


fake_users_db: dict[str, str] = {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


@app.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
def register(request: Request, data: AuthData):
    username = data.username
    password = data.password

    for existing_username in fake_users_db.keys():
        if secrets.compare_digest(existing_username, username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            )

    fake_users_db[username] = hash_password(password)
    return {"message": "New user created"}


@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, data: AuthData):
    username = data.username
    password = data.password

    found_username = None
    stored_hash = None

    for existing_username, hashed_password in fake_users_db.items():
        if secrets.compare_digest(existing_username, username):
            found_username = existing_username
            stored_hash = hashed_password
            break

    if found_username is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not verify_password(password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
        )

    token = create_access_token(found_username)
    return {"access_token": token, "token_type": "bearer"}


bearer_scheme = HTTPBearer(auto_error=False)

@app.get("/protected_resource")
def protected_resource(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"message": f"Access granted for {username}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)