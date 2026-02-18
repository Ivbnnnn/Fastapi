from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import uvicorn
from pathlib import Path
from models import User, UserAge, CalcRequest, Feedback

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

@app.get('/test')
async def test():
    return {"message": "Добро пожаловать в моё приложение FastAPI!"}

@app.get('/')
async def index():
    file_path = BASE_DIR / "index.html"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(file_path)

@app.post('/calculate')
async def calculate(req: CalcRequest):
    return {"result": req.num1 + req.num2}

user = User(id=1, name="Ivan Ivanov")
@app.get('/users', response_model=User)
async def users():
    return user

@app.post('/user')
async def user_adult(payload: UserAge):
    is_adult = payload.age >= 18
    return {"name": payload.name, "age": payload.age, "is_adult": is_adult}

feedbacks = []

@app.post('/feedback')
async def feedback(feedback: Feedback):
    feedbacks.append({"name": feedback.name, "message": feedback.message})
    print("All feedbacks:", feedbacks)
    return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён."}

if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8000)
