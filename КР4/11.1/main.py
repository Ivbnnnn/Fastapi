from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI()

users: dict[int, dict] = {}


class UserCreate(BaseModel):
    username: str
    email: EmailStr


@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    user_id = len(users) + 1

    users[user_id] = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
    }

    return users[user_id]


@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = users.get(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    user = users.pop(user_id, None)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted", "user": user}