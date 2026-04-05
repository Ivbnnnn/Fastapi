import os
import secrets
from typing import Annotated, Dict

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("MODE", "").upper()

if MODE not in {"DEV", "PROD"}:
    raise RuntimeError("MODE must be either DEV or PROD")

DOCS_USER = os.getenv("DOCS_USER", "")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "")

if MODE == "DEV" and (not DOCS_USER or not DOCS_PASSWORD):
    raise RuntimeError("In DEV mode DOCS_USER and DOCS_PASSWORD must be set")


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

class UserBase(BaseModel):
    username: str

class User(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

fake_users_db: Dict[str, UserInDB] = {}

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def auth_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> UserBase:
    user = fake_users_db.get(credentials.username)

    if not user:        
        secrets.compare_digest(credentials.username, "fakeuser")
        try:
            verify_password(credentials.password, "$2b$12$C6UzMDM.H6dfI/f/IKcEeO3nX6c1v5Wz4Q5f0mK3Qj0u2xS8JmW6K")
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    username_ok = secrets.compare_digest(credentials.username, user.username)
    password_ok = verify_password(credentials.password, user.hashed_password)

    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return UserBase(username=user.username)


@app.post("/register")
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already exists")

    fake_users_db[user.username] = UserInDB(
        username=user.username,
        hashed_password=get_password_hash(user.password),
    )
    return {"message": f"User '{user.username}' successfully registered."}

@app.get("/login")
def login(user: UserBase = Depends(auth_user)):
    return {"message": f"Welcome, {user.username}!"}

docs_security = HTTPBasic()

def auth_docs_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(docs_security)],
):
    username_ok = secrets.compare_digest(credentials.username, DOCS_USER)
    password_ok = secrets.compare_digest(credentials.password, DOCS_PASSWORD)

    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect docs credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

if MODE == "DEV":
    @app.get("/docs", include_in_schema=False, dependencies=[Depends(auth_docs_user)])
    async def custom_docs():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="API Docs",
        )

    @app.get("/openapi.json", include_in_schema=False, dependencies=[Depends(auth_docs_user)])
    async def custom_openapi():
        return JSONResponse(app.openapi())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)