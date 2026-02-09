from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str
    age:int

class Feedback(BaseModel):
    name: str
    message :str

    @field_validator("message")
    def no_cringe(cls, v):
        v= v.lower()
        if ('кринж' in v or 'рофл' in v or 'вайб' in v):
            raise ValueError("Использование недопустимых слов")
        return v
    
