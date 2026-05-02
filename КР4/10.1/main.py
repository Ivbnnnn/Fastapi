from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI()


class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int


class CustomExceptionA(Exception):
    def __init__(self, message: str = "Условие не выполнено"):
        self.message = message
        self.status_code = 400


class CustomExceptionB(Exception):
    def __init__(self, message: str = "Ресурс не найден"):
        self.message = message
        self.status_code = 404


@app.exception_handler(CustomExceptionA)
async def custom_exception_a_handler(
    request: Request,
    exc: CustomExceptionA,
):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="CustomExceptionA",
            message=exc.message,
            status_code=exc.status_code,
        ).model_dump(),
    )


@app.exception_handler(CustomExceptionB)
async def custom_exception_b_handler(
    request: Request,
    exc: CustomExceptionB,
):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="CustomExceptionB",
            message=exc.message,
            status_code=exc.status_code,
        ).model_dump(),
    )


@app.get("/check-age")
async def check_age(age: int):
    if age < 18:
        raise CustomExceptionA("Возраст должен быть не меньше 18 лет")

    return {"message": "Доступ разрешён"}


@app.get("/products/{product_id}")
async def get_product(product_id: int):
    products = {
        1: {"id": 1, "title": "Laptop", "price": 1200},
        2: {"id": 2, "title": "Phone", "price": 800},
    }

    product = products.get(product_id)

    if product is None:
        raise CustomExceptionB("Товар с таким id не найден")

    return product


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app")