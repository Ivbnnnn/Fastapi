from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
from models import User


app = FastAPI()

user = User(
    id=1,
    name="Ivan"
)


@app.get('/users', response_model=User)
async def index():
    return user



if __name__ == "__main__":
    uvicorn.run(app, 
                host='127.0.0.1',
                port=8000)