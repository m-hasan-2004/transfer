Alright! Let me explain JWT authentication in **FastAPI** in a **very simple** way.  

---

### **What is JWT?**  
JWT (JSON Web Token) is a way to **securely** allow users to log in.  
- When a user logs in, they receive a **token** (a long string of letters & numbers).  
- Every time they make a request, they send this **token** to prove they are allowed.  
- The server **checks** the token to confirm if it is valid.  

---

### **Steps to Add JWT Authentication in FastAPI**
1. **Install the necessary libraries**  
   Run this command in your terminal:  
   ```bash
   pip install fastapi pyjwt passlib[bcrypt]
   ```
   - `fastapi` → The framework.  
   - `pyjwt` → Handles JWT token creation & verification.  
   - `passlib[bcrypt]` → Hashes passwords securely.

---

### **1. User Signup (Register)**  
**What happens here?**  
- The user sends a username, email, and password.  
- We **store** the user’s information **with a hashed password** (not plain text).  

**Code:**
```python
from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI()

# Fake database (in-memory storage for testing)
fake_db = {}

# Hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

def hash_password(password: str):
    return pwd_context.hash(password)

@app.post("/signup")
def signup(user: UserCreate):
    if user.username in fake_db:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = hash_password(user.password)
    fake_db[user.username] = {"email": user.email, "password": hashed_password}

    return {"message": "User registered successfully"}
```

✅ **Try this in Postman or CURL**  
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/signup' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "mypassword"
  }'
```

---

### **2. User Login (Get JWT Token)**  
**What happens here?**  
- The user enters their **username & password**.  
- If correct, we generate a **JWT token** and return it.  

**Code:**
```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/login")
def login(user: UserCreate):
    stored_user = fake_db.get(user.username)

    if not stored_user or not pwd_context.verify(user.password, stored_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

✅ **Try this in Postman or CURL**  
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/login' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "mypassword"
  }'
```
**Response:**  
```json
{
  "access_token": "your_jwt_token_here",
  "token_type": "bearer"
}
```
👉 **Copy the token!** You will need it to access protected routes.

---

### **3. Protect Routes Using JWT**  
**What happens here?**  
- The user sends the **JWT token** in the request header.  
- If the token is **valid**, they can access the route.  
- If the token is **invalid or missing**, they get denied.

**Code:**
```python
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    user_data = verify_access_token(token)
    return {"message": f"Hello {user_data['sub']}, welcome to the protected route!"}
```

✅ **Try this in Postman or CURL**  
Replace `YOUR_JWT_TOKEN_HERE` with the token from the login response.

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/protected' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN_HERE'
```

If the token is valid, you will see:  
```json
{
  "message": "Hello john, welcome to the protected route!"
}
```
If the token is missing or invalid, you get an error.

---

### **Summary (Step-by-Step Flow)**
✅ **Step 1**: User **signs up** → We **save** their info in a database.  
✅ **Step 2**: User **logs in** → If correct, they get a **JWT token**.  
✅ **Step 3**: User uses the **JWT token** to access **protected routes**.  

Now, your FastAPI app has **JWT authentication**! 🎉  

Let me know if anything is unclear! 🚀
