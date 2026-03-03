from pydantic import BaseModel, EmailStr
from typing import Optional
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None
    is_subscribed:Optional[bool] = None