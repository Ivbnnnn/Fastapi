from datetime import datetime, timedelta, timezone
from typing import Annotated, Callable, Literal

import secrets
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext

app = FastAPI()

SECRET_KEY = "change-me-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

ROLE_ADMIN = "admin"
ROLE_USER = "user"
ROLE_GUEST = "guest"
ALLOWED_ROLES = {ROLE_ADMIN, ROLE_USER, ROLE_GUEST}

fake_users_db: dict[str, dict[str, str]] = {}

fake_resources = [
    {"id": 1, "name": "Public item"},
    {"id": 2, "name": "Another item"},
]


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: Literal["admin", "user", "guest"] = "guest"


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    username: str
    role: str


class ResourceCreate(BaseModel):
    name: str


class ResourceUpdate(BaseModel):
    name: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(username: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "role": role, "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]
) -> CurrentUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(credentials.credentials)
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
    role = payload.get("role")

    if not username or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = fake_users_db.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(username=user["username"], role=user["role"])


def require_roles(*allowed_roles: str) -> Callable:
    def dependency(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return current_user

    return dependency


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    for existing_username in fake_users_db.keys():
        if secrets.compare_digest(existing_username, data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            )

    fake_users_db[data.username] = {
        "username": data.username,
        "hashed_password": hash_password(data.password),
        "role": data.role,
    }
    return {"message": "New user created"}


@app.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    found_user = None

    for username, user in fake_users_db.items():
        if secrets.compare_digest(username, data.username):
            found_user = user
            break

    if found_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not verify_password(data.password, found_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
        )

    token = create_access_token(found_user["username"], found_user["role"])
    return {"access_token": token, "token_type": "bearer"}


@app.get("/protected_resource")
def protected_resource(
    current_user: Annotated[CurrentUser, Depends(require_roles(ROLE_ADMIN, ROLE_USER))]
):
    return {
        "message": f"Access granted to {current_user.username}",
        "role": current_user.role,
    }


@app.get("/resources")
def read_resources(
    current_user: Annotated[CurrentUser, Depends(require_roles(ROLE_ADMIN, ROLE_USER, ROLE_GUEST))]
):
    return {"items": fake_resources, "role": current_user.role}


@app.post("/resources")
def create_resource(
    data: ResourceCreate,
    current_user: Annotated[CurrentUser, Depends(require_roles(ROLE_ADMIN))]
):
    new_id = max(item["id"] for item in fake_resources) + 1 if fake_resources else 1
    item = {"id": new_id, "name": data.name}
    fake_resources.append(item)
    return {"message": "Resource created", "item": item}


@app.patch("/resources/{resource_id}")
def update_resource(
    resource_id: int,
    data: ResourceUpdate,
    current_user: Annotated[CurrentUser, Depends(require_roles(ROLE_ADMIN, ROLE_USER))]
):
    for item in fake_resources:
        if item["id"] == resource_id:
            item["name"] = data.name
            return {"message": "Resource updated", "item": item}

    raise HTTPException(status_code=404, detail="Resource not found")


@app.delete("/resources/{resource_id}")
def delete_resource(
    resource_id: int,
    current_user: Annotated[CurrentUser, Depends(require_roles(ROLE_ADMIN))]
):
    for idx, item in enumerate(fake_resources):
        if item["id"] == resource_id:
            deleted = fake_resources.pop(idx)
            return {"message": "Resource deleted", "item": deleted}

    raise HTTPException(status_code=404, detail="Resource not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)