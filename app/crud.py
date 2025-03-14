# crud.py

from .models import UserCreate
from .security import hash_password

# Fake DB for demonstration purposes
fake_db = {}

def create_user(user: UserCreate):
    if user.username in fake_db:
        raise Exception("Username already taken")
    hashed_password = hash_password(user.password)
    fake_db[user.username] = {"email": user.email, "password": hashed_password}
    return fake_db[user.username]

def get_user_by_username(username: str):
    return fake_db.get(username)
