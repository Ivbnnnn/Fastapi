# models.py (Pydantic v2 style)
from pydantic import BaseModel, Field, field_validator, ValidationError
import re

class User(BaseModel):
    id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1)

class UserAge(BaseModel):
    name: str = Field(..., min_length=1)
    age: int = Field(..., ge=0)

class CalcRequest(BaseModel):
    num1: int
    num2: int

class Feedback(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=500)

    @field_validator("message")
    @classmethod
    def forbidden_bad_words(cls, v: str) -> str:        
        forbidden = ["кринж", "рофл", "вайб"]
        low = v.lower()
        for word in forbidden:
            if word in low:
                raise ValueError("Использование недопустимых слов")
        return v
