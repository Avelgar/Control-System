from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta
import os

from .database import get_db, engine, Base
from .models import User
from .schemas import UserCreate, UserLogin, UserResponse, Token
from .auth import (
    authenticate_user, create_access_token, 
    get_current_active_user, get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Создаем таблицы
try:
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы")
except SQLAlchemyError as e:
    print(f"Ошибка при создании таблиц: {e}")

app = FastAPI(title="Construction Control System API", version="1.0.0")

# Настраиваем обслуживание статических файлов из папки frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000", 
        "http://127.0.0.1:8000",
        "http://blue.fnode.me:25526",
        "http://91.222.239.132:25526",
        "http://blue.fnode.me",
        "http://91.222.239.132"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/", response_class=FileResponse)
async def read_root():
    return FileResponse("../frontend/index.html")

@app.get("/css/{file_path:path}", response_class=FileResponse)
async def serve_css(file_path: str):
    full_path = f"../frontend/css/{file_path}"
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(full_path)

@app.get("/js/{file_path:path}", response_class=FileResponse)
async def serve_js(file_path: str):
    full_path = f"../frontend/js/{file_path}"
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(full_path)

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "database": "MySQL",
        "version": "1.0.0",
        "server": "blue.fnode.me:25526"
    }

# API endpoints
@app.post("/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = get_user_by_username(db, username=user.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        db_user = get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        return create_user(db=db, user=user)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error")

@app.post("/auth/login", response_model=Token)
def login(form_data: UserLogin, db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error")

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=25526)