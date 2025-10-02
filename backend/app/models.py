from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import enum

class DefectStatus(enum.Enum):
    NEW = "новая"
    IN_PROGRESS = "в работе" 
    UNDER_REVIEW = "на проверке"
    CLOSED = "закрыта"
    CANCELLED = "отменена"

class PriorityLevel(enum.Enum):
    LOW = "низкий"
    MEDIUM = "средний"
    HIGH = "высокий"
    CRITICAL = "критический"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    login = Column(String(100), unique=True, index=True, nullable=False)
    fio = Column(String(200), nullable=False)
    password_hash = Column(String(255), nullable=False)
    reg_token = Column(String(255), nullable=True)
    role = Column(String(50), default="observer", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    address = Column(String(500))
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(50), default="активный")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("User")

class ProjectStage(Base):
    __tablename__ = "project_stages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    sequence = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(50), default="активный")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project")

class Defect(Base):
    __tablename__ = "defects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project_stage_id = Column(Integer, ForeignKey("project_stages.id"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    priority = Column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM)
    status = Column(Enum(DefectStatus), default=DefectStatus.NEW)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    due_date = Column(Date)
    actual_completion_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project")
    stage = relationship("ProjectStage")
    assignee = relationship("User", foreign_keys=[assigned_to])
    reporter = relationship("User", foreign_keys=[reported_by])

class DefectComment(Base):
    __tablename__ = "defect_comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    defect_id = Column(Integer, ForeignKey("defects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    defect = relationship("Defect")
    user = relationship("User")

class DefectAttachment(Base):
    __tablename__ = "defect_attachments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    defect_id = Column(Integer, ForeignKey("defects.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(100))
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    defect = relationship("Defect")
    uploader = relationship("User")

class DefectHistory(Base):
    __tablename__ = "defect_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    defect_id = Column(Integer, ForeignKey("defects.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    defect = relationship("Defect")
    user = relationship("User")