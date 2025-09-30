from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session
import os
from urllib.parse import quote

from .database import get_db, engine, Base
from .models import User
from .schemas import UserCreate, UserResponseAuth
from .auth import get_password_hash, generate_registration_token, send_registration_email, check_password, check_reg_data

# Создаем таблицы
Base.metadata.create_all(bind=engine)
print("Таблица users создана")

app = FastAPI(title="Construction Control System API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_user_by_login(db: Session, login: str):
    return db.query(User).filter(User.login == login).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_token(db: Session, token: str):
    return db.query(User).filter(User.reg_token == token).first()


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
    return {"status": "healthy", "message": "Service is running"}

@app.get("/verify")
def verify_register(request: Request, db: Session = Depends(get_db)):
    # Получаем токен из query параметров
    token = request.query_params.get("token")
    
    if not token:
        # Если токена нет, перенаправляем на главную с сообщением об ошибке
        error_message = "Токен верификации не предоставлен"
        return RedirectResponse(url=f"/?error={quote(error_message)}")
    
    # Ищем пользователя по токену
    user = get_user_by_token(db, token)
    
    if not user:
        # Если пользователь не найден, перенаправляем с ошибкой
        error_message = "Неверный или устаревший токен верификации"
        return RedirectResponse(url=f"/?error={quote(error_message)}")
    
    # Удаляем токен у пользователя (устанавливаем в None)
    user.reg_token = None
    db.commit()
    
    # Перенаправляем на главную с сообщением об успехе
    success_message = f"Аккаунт {user.email} успешно подтвержден!"
    return RedirectResponse(url=f"/?success={quote(success_message)}")

@app.post("/auth/register", response_model=UserResponseAuth)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if not(user.email and user.username and user.full_name and user.password and user.confirm_password):
        raise HTTPException(status_code=400, detail="Недостаточно данных")
    
    is_data_bad = check_reg_data(user.email, user.username, user.full_name)
    if is_data_bad:
        raise HTTPException(status_code=400, detail=is_data_bad)
    
    # Проверка существования логина
    existing_user = get_user_by_login(db, login=user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Логин уже занят")
    
    # Проверка существования email
    existing_email = get_user_by_email(db, email=user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    # Проверка совпадения паролей
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")
    
    # Проверка сложности пароля
    password_error = check_password(user.password)
    if password_error:
        raise HTTPException(status_code=400, detail=password_error)
    
    # Проверка длины пароля
    if len(user.password.encode('utf-8')) > 72:
        raise HTTPException(status_code=400, detail="Пароль слишком длинный")
    
    # Генерация регистрационного токена
    reg_token = generate_registration_token()
    
    try:
        # ПЕРВОЕ: Пытаемся отправить письмо
        send_registration_email(user.email, reg_token)
        
        # ВТОРОЕ: Если отправка успешна, создаем пользователя
        db_user = User(
            email=user.email,
            login=user.username,
            fio=user.full_name,
            password_hash=get_password_hash(user.password),
            reg_token=reg_token,
            role="observer"
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {"detail":"Подтвердите почту"}
        
    except Exception as e:
        # Если отправка письма не удалась, НЕ создаем пользователя
        raise HTTPException(status_code=500, detail="Не можем отправить письмо, попробуйте позже")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=25526)