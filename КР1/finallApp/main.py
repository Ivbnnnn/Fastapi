from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
from models import User, Feedback

app = FastAPI()


@app.get('/test')
async def test():
    return {"message": "Добро пожаловать в моё приложение FastAPI!"}

@app.get('/')
async def index():
    return FileResponse("КР1/1.2/index.html")

@app.post('/calculate')
async def index(num1, num2):
    return{"result":  int(num1)+int(num2)}

user = User(
    age=1, # id
    name="Ivan"
)
@app.get('/users', response_model=User)
async def index():
    return user

@app.get('/user')
async def index(name, age):
    adult = False
    if (int(age)>=18):adult = True
    return {"name": name, "age": age, "adult": adult }






feedbacks = []
@app.get('/user')
async def index(name, age):
    adult = False
    if (int(age)>=18):adult = True
    return {"name": name, "age": age, "adult": adult }



@app.post('/feedback')
async def feedback(feedback: Feedback):
    feedbacks.append(feedback.message)
    print(feedbacks)
    return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён."}


if __name__ == "__main__":
    uvicorn.run(app, 
                host='127.0.0.1',
                port=8000)