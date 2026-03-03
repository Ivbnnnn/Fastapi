import uvicorn
import uuid
import time
import hmac
import hashlib
from fastapi import FastAPI, Response, Request, Depends, Cookie
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from models import UserCreate
app = FastAPI()
SECRET_KEY = "FDSJKFHdsjvbc839021ejfvdJSKAD(*Y)(#@!!fgudisfds12h3j21bjkfds8yVXJZKVBJFDSAJH)"

name = "ivan"
password = "password"


def make_signature(user_id: str, timestamp: int) -> str:
    msg = f"{user_id}.{timestamp}".encode()
    return hmac.new(SECRET_KEY.encode(), msg, hashlib.sha256).hexdigest()

def make_token(user_id: str, timestamp: int) -> str:
    sig = make_signature(user_id, timestamp)
    return f"{user_id}.{timestamp}.{sig}"

def verify_token(token: str):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return "invalid", None
        user_id, ts_str, sig = parts
        timestamp = int(ts_str)
    except Exception:
        return "invalid", None

    expected = make_signature(user_id, timestamp)
    if not hmac.compare_digest(expected, sig):
        return "invalid", None

    now = int(time.time())
    if timestamp > now:
        return "invalid", None

    age = now - timestamp
    if age >= 300:
        return "expired", None
    return "ok", (user_id, age)

@app.post("/login")
async def login(user: UserCreate, response: Response):
    if user.name == name and user.password == password:
        user_id = str(uuid.uuid4())
        now = int(time.time())
        token = make_token(user_id, now)
        response.set_cookie(
            key="session_token",
            value=token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=300
        )
        return {"message": "passed"}
    else:
        return JSONResponse(status_code=401, content={"message":"Invalid name/password"})

async def check_user(response: Response, session_token: str = Cookie(default=None, alias="session_token")):
    if session_token is None:
        return "expired", None

    status, payload = verify_token(session_token)
    if status != "ok":
        return status, None

    user_id, age = payload
    now = int(time.time())
    if 180 <= age < 300:
        new_token = make_token(user_id, now)
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=300
        )
    return "ok", user_id

@app.get("/user")
async def profile(check = Depends(check_user)):
    status, user_id = check
    if status == "ok":
        return {"message":"passed_user"}
    elif status == "expired":
        return JSONResponse(status_code=401, content={"message":"Session expired"})
    else:  
        return JSONResponse(status_code=401, content={"message":"Invalid session"})

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8000, host="127.0.0.1")