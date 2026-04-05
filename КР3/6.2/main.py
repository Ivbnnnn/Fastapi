from typing import Annotated, Dict
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
import secrets

app = FastAPI()
security = HTTPBasic()

class UserBase(BaseModel):
    username: str

class User(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

fake_users_db: Dict[str, UserInDB] = {}

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def auth_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> UserBase:
    user = fake_users_db.get(credentials.username)

    if not user:
        # одинаковая по времени "пустая" проверка
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

    if not verify_password(credentials.password, user.hashed_password):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)