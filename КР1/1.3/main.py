from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI()

@app.post('/calculate')
async def index(num1, num2):
    return{"result":  int(num1)+int(num2)}



if __name__ == "__main__":
    uvicorn.run(app, 
                host='127.0.0.1',
                port=8000)