from fastapi import FastAPI
import uvicorn
from models import UserCreate
app = FastAPI()


@app.post("/create_user")
async def create_user(user: UserCreate):
    return user



if __name__  == "__main__":
    
    uvicorn.run("main:app", reload=True, port=8000, host="127.0.0.1")