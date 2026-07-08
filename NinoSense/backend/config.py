import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ninosense-super-secret-key-1337-prod-gov')
    
    # Database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'ninosense.db')
    
    # Google OAuth 2.0 Credentials (Set in environmental variables)
    # If not present, we will fallback to simulation mode automatically
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', None)
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', None)
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    
    # Notification configurations
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'localhost')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 1025))
    EMAIL_SENDER = os.environ.get('EMAIL_SENDER', 'alerts@ninosense.gov')
