import uvicorn
from models import UserCreate
from fastapi import FastAPI, Response, Request, Depends, Cookie
import uuid

app = FastAPI()

name, password = "ivan", "password"
session_token="6aa52172-0683-4e53-8f2e-a7c0fd23fd50"

@app.post("/login")
async def create_user(
    user : UserCreate, 
    response: Response
):
    if user.name == name and user.password:
        response.set_cookie(
            secure=False,
            httponly=True,
            value=session_token,
            key="session_token",
            samesite="lax"
        )
    return {"message":"passed"} 

async def check_user(value = Cookie(default=None, alias="session_token")):
    if value == session_token:
        return True
    else:
        return False
    
    
@app.get("/user")
async def user(
    response: Response,
    passed: bool = Depends(check_user)
):
    if passed:
        return {"message":"passed2"} 
    else:
        response.status_code=401
        return {"message": "Unauthorized"}





if __name__  == "__main__":
    
    uvicorn.run("main:app", reload=True, port=8000, host="127.0.0.1")