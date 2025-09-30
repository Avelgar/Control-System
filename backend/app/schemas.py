from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    confirm_password: str

class UserResponseAuth(BaseModel):
    detail: str