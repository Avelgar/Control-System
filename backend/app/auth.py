import re
from passlib.context import CryptContext
import secrets
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_password(password):
    if len(password) < 8:
        return "Пароль должен содержать минимум 8 символов"
    if not any(char.isdigit() for char in password):
        return "Пароль должен содержать хотя бы одну цифру"
    if not any(char.isalpha() for char in password):
        return "Пароль должен содержать хотя бы одну букву"
    if not any(char.isupper() for char in password):
        return "Пароль должен содержать хотя бы одну заглавную букву"
    if not any(char.islower() for char in password):
        return "Пароль должен содержать хотя бы одну строчную букву"
    return None

def check_reg_data(email, login, full_name):
    # Проверка email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return "Неверный формат email"
    
    # Проверка логина
    if len(login) < 3:
        return "Логин должен содержать минимум 3 символа"
    if len(login) > 50:
        return "Логин слишком длинный (максимум 50 символов)"
    login_pattern = r'^[a-zA-Z0-9_]+$'
    if not re.match(login_pattern, login):
        return "Логин может содержать только латинские буквы, цифры и подчеркивание"
    
    # Проверка ФИО
    if len(full_name.strip()) < 2:
        return "ФИО слишком короткое"
    if len(full_name) > 100:
        return "ФИО слишком длинное (максимум 100 символов)"
    
    # Проверка на наличие только букв, пробелов и дефисов в ФИО
    name_pattern = r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$'
    if not re.match(name_pattern, full_name):
        return "ФИО может содержать только буквы, пробелы и дефисы"
    
    # Проверка что в ФИО есть хотя бы 2 слова (имя и фамилия)
    name_parts = full_name.strip().split()
    if len(name_parts) < 2:
        return "Укажите имя и фамилию"
    
    return None

def get_password_hash(password):
    if len(password.encode('utf-8')) > 72:
        raise ValueError("Password too long")
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def generate_registration_token():
    return secrets.token_urlsafe(32)

def send_registration_email(email: str, token: str):
    """Отправка email с регистрационным токеном"""
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.yandex.ru")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        if not all([smtp_username, smtp_password]):
            print(f"SMTP credentials not configured. Token for {email}: {token}")
            raise Exception("SMTP не настроен")
        
        subject = "Регистрация в системе СистемаКонтроля"
        body = f"""
        Добро пожаловать в систему СистемаКонтроля!
        
        Для завершения регистрации перейдите по ссылке:
        http://blue.fnode.me:25526/verify?token={token}
        
        Если вы не регистрировались в системе, проигнорируйте это письмо.
        
        С уважением,
        Команда СистемаКонтроля
        """
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = smtp_username
        msg['To'] = email
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            
        print(f"Registration email sent to {email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email to {email}: {str(e)}")
        raise Exception(f"Ошибка отправки email: {str(e)}")