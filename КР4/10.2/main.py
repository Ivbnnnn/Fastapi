from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, conint, constr


app = FastAPI()


class User(BaseModel):
    username: str
    age: conint(gt=18)
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = "Unknown"


class ValidationErrorResponse(BaseModel):
    error: str
    message: str
    details: list[dict]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content=ValidationErrorResponse(
            error="ValidationError",
            message="Ошибка валидации входных данных",
            details=exc.errors(),
        ).model_dump(),
    )


@app.post("/users")
async def create_user(user: User):
    return {
        "message": "Пользователь успешно создан",
        "user": user,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app")