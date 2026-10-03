import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-change-in-production'
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or b'2P-vFzXz5xK-19XWw0Lh5jJ3H1O2uO_X0k3NfQGz6aA=' # Default Fernet key for dev
    DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'securevault.db')
