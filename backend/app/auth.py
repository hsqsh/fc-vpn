from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# 用于模拟用户存储
fake_users = {}

class UserIn(BaseModel):
    username: str
    password: str

@router.post("/auth/register")
def register(user: UserIn):
    if user.username in fake_users:
        raise HTTPException(status_code=400, detail="User already exists")
    fake_users[user.username] = user.password
    return {"msg": "Register success"}

@router.post("/auth/login")
def login(user: UserIn):
    if user.username not in fake_users or fake_users[user.username] != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"msg": "Login success", "username": user.username}
