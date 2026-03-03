import uvicorn
import uuid
import time
import hmac
import hashlib
from fastapi import FastAPI, Response, Request, Depends, Cookie, Header
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from models import CommonHeaders
import re
from datetime import datetime


app = FastAPI()

def common_headers(
    Accept_Language: str = Header(...),
    User_Agent: str = Header(...),
) -> CommonHeaders:
    try:
        return CommonHeaders(Accept_Language=Accept_Language, User_Agent= User_Agent)
    except:
        raise HTTPException(status_code=400, detail={"message": "Invalid headers"})


@app.get("/headers")
async def profile(headers: CommonHeaders = Depends(common_headers)):
    return headers


@app.get("/info")
async def profile(
    response:Response,
    headers: CommonHeaders = Depends(common_headers)):
    response.headers.append("X-Server-Time", str(datetime.now()))
    return headers, {"message":"Добро пожаловать! Ваши заголовки успешно обработаны."}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8000, host="127.0.0.1")