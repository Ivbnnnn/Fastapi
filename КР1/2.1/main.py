from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
from models import User

app = FastAPI()

from models import Feedback

db = []
@app.get('/user')
async def index(name, age):
    adult = False
    if (int(age)>=18):adult = True
    return {"name": name, "age": age, "adult": adult }




@app.post('/feedback')
async def feedback(feedback: Feedback):
    db.append(feedback.message)
    print(db)
    return {
    "message": f"Feedback received. Thank you, {feedback.name}."
}



if __name__ == "__main__":
    uvicorn.run(app, 
                host='127.0.0.1',
                port=8000)