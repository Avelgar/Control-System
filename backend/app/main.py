from fastapi import FastAPI, Depends, HTTPException, Request, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
import os
from urllib.parse import quote
from datetime import datetime, timedelta
from typing import List, Optional

from .database import get_db, engine, Base
from . import models
from .models import User, Project, ProjectStage, Defect, DefectComment, DefectAttachment, DefectHistory
from .schemas import (
    UserCreate, UserLogin, UserResponseAuth, Token, UserProfile,
    ProjectCreate, Project,
    ProjectStageCreate, ProjectStage,
    DefectCreate, Defect, DefectUpdate,
    CommentCreate, Comment,
    AttachmentCreate, Attachment
)
from .auth import get_password_hash, generate_registration_token, send_registration_email, check_password, check_reg_data, verify_password, create_access_token, verify_token

# Создаем таблицы
Base.metadata.create_all(bind=engine)
print("Все таблицы созданы")

try:
    db = next(get_db())
    
    # Создаем тестового пользователя если его нет
    test_user = db.query(User).filter(User.email == "test@example.com").first()
    if not test_user:
        test_user = User(
            email="test@example.com",
            login="testuser",
            fio="Тестовый Пользователь",
            password_hash=get_password_hash("Test123!"),
            role="manager"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print("✅ Тестовый пользователь создан")
    
    # Создаем остальные тестовые данные
    from .test_data import create_test_data
    create_test_data(db)
    print("✅ Тестовые данные добавлены")
    
except Exception as e:
    print(f"⚠️ Тестовые данные не созданы: {e}")

app = FastAPI(title="Construction Control System API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Вспомогательные функции
def get_user_by_login(db: Session, login: str):
    return db.query(User).filter(User.login == login).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_token(db: Session, token: str):
    return db.query(User).filter(User.reg_token == token).first()

def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется аутентификация"
        )
    
    token = auth_header.replace("Bearer ", "")
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен"
        )
    
    email = payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен"
        )
    
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    
    if user.reg_token is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Подтвердите почту для доступа"
        )
    
    return user

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
    
@app.post("/auth/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    if not(user.login and user.password):
        raise HTTPException(status_code=400, detail="Недостаточно данных")
    
    # Определяем, это email или username
    if "@" in user.login:
        # Это email
        db_user = get_user_by_email(db, user.login)
    else:
        # Это username
        db_user = get_user_by_login(db, user.login)
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")
    
    # Проверяем, подтверждена ли почта
    if db_user.reg_token is not None:
        raise HTTPException(status_code=400, detail="Подтвердите почту перед входом")
    
    # Проверяем пароль
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")
    
    # Создаем JWT токен ТОЛЬКО с email
    access_token = create_access_token(
        data={"email": db_user.email}  # Только email, без login и role
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=25526)


@app.get("/main-page")
def main_page_html():
    """Страница main.html"""
    return FileResponse("../frontend/main.html")

# Также обновите endpoint /main для проверки аутентификации
@app.get("/main")
def main_page(request: Request, db: Session = Depends(get_db)):
    # Получаем токен из заголовков Authorization
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется аутентификация"
        )
    
    token = auth_header.replace("Bearer ", "")
    
    # Проверяем токен
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен"
        )
    
    # Получаем email из токена
    email = payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен"
        )
    
    # Проверяем существование пользователя в БД
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    
    # Проверяем, подтверждена ли почта
    if user.reg_token is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Подтвердите почту для доступа"
        )
    
    # Возвращаем успешный ответ с информацией о пользователе
    return {
        "status": "success", 
        "message": "Доступ разрешен",
        "user": {
            "email": user.email,
            "login": user.login,
            "full_name": user.fio,
            "role": user.role
        }
    }

@app.get("/api/projects", response_model=List[Project])
def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список проектов (доступно всем ролям)"""
    projects = db.query(models.Project).all()
    return projects

@app.get("/api/projects/{project_id}", response_model=Project)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить детальную информацию о проекте (доступно всем ролям)"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project

@app.get("/api/defects", response_model=List[Defect])
def get_defects(
    current_user: User = Depends(get_current_user),
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получить список дефектов с фильтрацией"""
    query = db.query(models.Defect)
    
    # Фильтрация по проекту
    if project_id:
        query = query.filter(models.Defect.project_id == project_id)
    
    # Фильтрация по статусу
    if status:
        query = query.filter(models.Defect.status == status)
    
    # Для инженеров показываем только их дефекты
    if current_user.role == "engineer":
        query = query.filter(
            (models.Defect.reported_by == current_user.id) | 
            (models.Defect.assigned_to == current_user.id)
        )
    
    defects = query.all()
    return defects

# 👷 ЭНДПОИНТЫ ДЛЯ ИНЖЕНЕРОВ
@app.post("/api/defects", response_model=Defect)
def create_defect(
    defect: DefectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать новый дефект (только инженеры и менеджеры)"""
    if current_user.role not in ["engineer", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания дефектов"
        )
    
    # Проверяем существование проекта
    project = db.query(Project).filter(Project.id == defect.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Создаем дефект
    db_defect = Defect(
        **defect.model_dump(),
        reported_by=current_user.id
    )
    
    db.add(db_defect)
    db.commit()
    db.refresh(db_defect)
    
    # Записываем в историю
    history = DefectHistory(
        defect_id=db_defect.id,
        field_name="created",
        old_value=None,
        new_value="Дефект создан",
        changed_by=current_user.id
    )
    db.add(history)
    db.commit()
    
    return db_defect

@app.patch("/api/defects/{defect_id}", response_model=Defect)
def update_defect(
    defect_id: int,
    defect_update: DefectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить дефект (инженеры - только свои, менеджеры - любые)"""
    db_defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not db_defect:
        raise HTTPException(status_code=404, detail="Дефект не найден")
    
    # Проверка прав
    if current_user.role == "engineer" and db_defect.reported_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете редактировать только свои дефекты"
        )
    
    # Обновляем поля
    update_data = defect_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(db_defect, field):
            old_value = str(getattr(db_defect, field))
            setattr(db_defect, field, value)
            
            # Записываем в историю
            history = DefectHistory(
                defect_id=defect_id,
                field_name=field,
                old_value=old_value,
                new_value=str(value),
                changed_by=current_user.id
            )
            db.add(history)
    
    db_defect.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_defect)
    
    return db_defect

@app.post("/api/comments", response_model=Comment)
def create_comment(
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Добавить комментарий к дефекту (инженеры и менеджеры)"""
    if current_user.role not in ["engineer", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для добавления комментариев"
        )
    
    # Проверяем существование дефекта
    defect = db.query(Defect).filter(Defect.id == comment.defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="Дефект не найден")
    
    # Для инженеров проверяем доступ к дефекту
    if current_user.role == "engineer" and defect.reported_by != current_user.id and defect.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете комментировать только свои дефекты"
        )
    
    db_comment = DefectComment(
        **comment.model_dump(),
        user_id=current_user.id
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment

# 👨‍💼 ЭНДПОИНТЫ ДЛЯ МЕНЕДЖЕРОВ
@app.post("/api/projects", response_model=Project)
def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать новый проект (только менеджеры)"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания проектов"
        )
    
    db_project = Project(
        **project.model_dump(),
        created_by=current_user.id
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return db_project

@app.post("/api/project-stages", response_model=ProjectStage)
def create_project_stage(
    stage: ProjectStageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать этап проекта (только менеджеры)"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания этапов проектов"
        )
    
    db_stage = ProjectStage(**stage.model_dump())
    
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    
    return db_stage

@app.get("/api/users", response_model=List[UserProfile])
def get_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список пользователей (только менеджеры)"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра списка пользователей"
        )
    
    users = db.query(User).filter(User.reg_token == None).all()
    return [
        UserProfile(
            email=user.email,
            login=user.login,
            full_name=user.fio,
            role=user.role
        )
        for user in users
    ]

# 📈 ЭНДПОИНТЫ ДЛЯ ОТЧЕТНОСТИ
@app.get("/api/reports/defects-statistics")
def get_defects_statistics(
    current_user: User = Depends(get_current_user),
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Получить статистику по дефектам (менеджеры и наблюдатели)"""
    if current_user.role not in ["manager", "observer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра статистики"
        )
    
    # Базовая статистика
    query = db.query(models.Defect)
    if project_id:
        query = query.filter(models.Defect.project_id == project_id)
    
    total_defects = query.count()
    new_defects = query.filter(models.Defect.status == "новая").count()
    in_progress_defects = query.filter(models.Defect.status == "в работе").count()
    closed_defects = query.filter(models.Defect.status == "закрыта").count()
    
    return {
        "total": total_defects,
        "new": new_defects,
        "in_progress": in_progress_defects,
        "closed": closed_defects,
        "completion_rate": round((closed_defects / total_defects * 100) if total_defects > 0 else 0, 2)
    }

# Статические файлы (остаются без изменений)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=25526)