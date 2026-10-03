from cryptography.fernet import Fernet
from flask import current_app

def get_fernet():
    key = current_app.config['ENCRYPTION_KEY']
    return Fernet(key)

def encrypt_password(password: str) -> str:
    f = get_fernet()
    return f.encrypt(password.encode('utf-8')).decode('utf-8')

def decrypt_password(encrypted_password: str) -> str:
    f = get_fernet()
    return f.decrypt(encrypted_password.encode('utf-8')).decode('utf-8')
