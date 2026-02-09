from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
from models import User


app = FastAPI()




@app.get('/user')
async def index(name, age):
    adult = False
    if (int(age)>=18):adult = True
    return {"name": name, "age": age, "adult": adult }



if __name__ == "__main__":
    uvicorn.run(app, 
                host='127.0.0.1',
                port=8000)