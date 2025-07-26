import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}"
        f"@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '3306')}/{os.environ.get('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PESAPAL_CONSUMER_KEY = os.environ.get('PESAPAL_CONSUMER_KEY')
    PESAPAL_CONSUMER_SECRET = os.environ.get('PESAPAL_CONSUMER_SECRET')
    
    # Production settings
    PESAPAL_IPN_SECRET = os.environ.get('PESAPAL_IPN_SECRET', 'your-ipn-secret-key')
    PESAPAL_BASE_URL = os.environ.get('PESAPAL_BASE_URL', 'https://pay.pesapal.com/v3/api')
    
    # API Base URL for frontend
    API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:5000')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # Security settings
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_REQUESTS = int(os.environ.get('RATE_LIMIT_REQUESTS', '100'))
    RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', '3600'))  # 1 hour 
    PESAPAL_NOTIFICATION_ID = os.environ.get('PESAPAL_NOTIFICATION_ID', '4ad16ada-f09b-4b45-8c18-db86b60a879d') 