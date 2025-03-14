# main.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from .security import create_access_token, verify_access_token, hash_password, verify_password
from .crud import create_user, get_user_by_username
from .models import UserCreate, UserOut
from fastapi.security import OAuth2PasswordBearer

# Initialize FastAPI app
app = FastAPI()

# OAuth2 scheme (for extracting token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/signup", response_model=UserOut)
def signup(user: UserCreate):
    try:
        created_user = create_user(user)
        return UserOut(username=user.username, email=user.email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(user: UserCreate):
    stored_user = get_user_by_username(user.username)

    if not stored_user or not verify_password(user.password, stored_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Protect routes with JWT token
@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"message": f"Hello {username}, you have access to this route!"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
