from pydantic import BaseModel, EmailStr
from typing import Optional
class UserCreate(BaseModel):
    name: str
    password: str