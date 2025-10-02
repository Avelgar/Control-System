from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    login: str
    password: str

class UserResponseAuth(BaseModel):
    detail: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserProfile(BaseModel):
    email: str
    login: str
    full_name: str
    role: str
    id: Optional[int] = None

    class Config:
        from_attributes = True

# Простые схемы для проектов
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = "активный"

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Схемы для этапов проекта
class ProjectStageBase(BaseModel):
    name: str
    description: Optional[str] = None
    sequence: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = "активный"

class ProjectStageCreate(ProjectStageBase):
    project_id: int

class ProjectStage(ProjectStageBase):
    id: int
    project_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Схемы для дефектов
class DefectBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "средний"
    status: str = "новая"
    due_date: Optional[date] = None

class DefectCreate(DefectBase):
    project_id: int
    project_stage_id: Optional[int] = None
    assigned_to: Optional[int] = None

class DefectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[date] = None
    actual_completion_date: Optional[date] = None

class Defect(DefectBase):
    id: int
    project_id: int
    project_stage_id: Optional[int] = None
    assigned_to: Optional[int] = None
    reported_by: int
    actual_completion_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Схемы для комментариев
class CommentBase(BaseModel):
    comment: str

class CommentCreate(CommentBase):
    defect_id: int

class Comment(CommentBase):
    id: int
    defect_id: int
    user_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Схемы для вложений
class AttachmentBase(BaseModel):
    filename: str
    file_path: str
    file_type: Optional[str] = None

class AttachmentCreate(AttachmentBase):
    defect_id: int

class Attachment(AttachmentBase):
    id: int
    defect_id: int
    uploaded_by: int
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True