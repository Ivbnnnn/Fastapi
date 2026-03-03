import uvicorn
from models import UserCreate
from fastapi import FastAPI, Response, Request, Depends, Cookie
from fastapi.exceptions import HTTPException
import uuid
from itsdangerous import URLSafeSerializer, BadSignature
app = FastAPI()
SECRET_KEY = "FDSJKFHdsjvbc839021ejfvdJSKAD(*Y)(#@!!fgudisfds12h3j21bjkfds8yVXJZKVBJFDSAJH)"

name = "ivan"
password = "password"
TOKEN=""
USER_ID=""

@app.post("/login")
async def create_user(
    user : UserCreate, 
    response: Response
):
    if user.name == name and user.password == password:
        u_uid = str(uuid.uuid4())
        global USER_ID
        USER_ID = u_uid
        serializer = URLSafeSerializer(SECRET_KEY)
        session_token = serializer.dumps(u_uid)
        global TOKEN
        TOKEN = session_token
        response.set_cookie(
            secure=False,
            httponly=True,
            value=session_token,
            key="session_token",
            samesite="lax",
            max_age=30
        )
        return {"message":"passed"}
    else:        
        raise HTTPException(status_code=401, detail="incorrect login/password")

async def check_user(value = Cookie(default=None, alias="session_token")):
    serializer = URLSafeSerializer(SECRET_KEY)
    if value == None:
        raise HTTPException(status_code=401, detail="you must have session_token!")
    try:
        original_user_id = serializer.loads(value)
    except:
        raise HTTPException(status_code=401, detail="incorrect signature")
    if original_user_id == USER_ID:
        return True
    else:
        return False
    
    
@app.get("/user")
async def user(
    response: Response,
    passed: bool = Depends(check_user)
):
    if passed:
        return {"message":"passed_user"} 
    else:
        response.status_code=401
        return {"message": "Unauthorized"}





if __name__  == "__main__":
    
    uvicorn.run("main:app", reload=True, port=8000, host="127.0.0.1")