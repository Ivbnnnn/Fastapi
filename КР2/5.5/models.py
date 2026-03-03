from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from fastapi import Header
import re
LANG = re.compile(r'^([a-z]{2}(-[A-Z]{2})?)(,[a-z]{2}(-[A-Z]{2})?(;q=0\.\d+)*)*$')
class CommonHeaders(BaseModel):
    User_Agent: str 
    Accept_Language: str = Header(..., regex=LANG)