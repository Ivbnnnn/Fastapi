import uvicorn
import uuid
import time
import hmac
import hashlib
from fastapi import FastAPI, Response, Request, Depends, Cookie
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
import re


app = FastAPI()

LANG = re.compile(r'^([a-z]{2}(-[A-Z]{2})?)(,[a-z]{2}(-[A-Z]{2})?(;q=0\.\d+)*)*$')

@app.get("/headers")
async def profile(request: Request):
    if request.headers.get("User-agent") is None or request.headers.get("Accept-Language") is None or not LANG.match(request.headers.get("Accept-Language")):
        raise HTTPException(status_code=400, detail="no/invalid User-agent or  Accept-Language")
    return {"User-agent": request.headers.get("User-agent"), "Accept-Language":request.headers.get("Accept-Language")}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8000, host="127.0.0.1")