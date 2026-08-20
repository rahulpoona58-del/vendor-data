import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if it exists
dotenv_path = BASE_DIR / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# Safe Environment Variable Parsing Helpers
def get_env_str(name: str, default: str) -> str:
    """Safely retrieves a string environment variable, returning default if missing, empty, or whitespace."""
    val = os.getenv(name)
    if val is None or not str(val).strip():
        return default
    return str(val).strip()

def get_int_env(name: str, default: int) -> int:
    """Safely retrieves an integer environment variable, returning default if missing, empty, or unparseable."""
    val = os.getenv(name)
    if val is None or not str(val).strip():
        return default
    try:
        return int(str(val).strip())
    except (TypeError, ValueError):
        return default

def get_float_env(name: str, default: float) -> float:
    """Safely retrieves a float environment variable, returning default if missing, empty, or unparseable."""
    val = os.getenv(name)
    if val is None or not str(val).strip():
        return default
    try:
        return float(str(val).strip())
    except (TypeError, ValueError):
        return default

def get_bool_env(name: str, default: bool) -> bool:
    """Safely retrieves a boolean environment variable, returning default if missing, empty, or invalid."""
    val = os.getenv(name)
    if val is None or not str(val).strip():
        return default
    s = str(val).strip().lower()
    if s in ('true', '1', 't', 'yes', 'y', 'enabled'):
        return True
    if s in ('false', '0', 'f', 'no', 'n', 'disabled'):
        return False
    return default

# Environment detection for Vercel serverless runtime
IS_VERCEL = bool(get_env_str('VERCEL', '') or get_env_str('VERCEL_ENV', ''))

# Resolve default SQLite database path (prefer instance/vendors.db containing 500 records)
SRC_DB_PATH = BASE_DIR / 'instance' / 'vendors.db'
if not SRC_DB_PATH.exists():
    SRC_DB_PATH = BASE_DIR / 'instance' / 'vendor_trust.db'

if IS_VERCEL:
    # On Vercel, copy database to /tmp to ensure writable runtime access
    TMP_DB_PATH = Path('/tmp/vendors.db')
    if not TMP_DB_PATH.exists() and SRC_DB_PATH.exists():
        import shutil
        try:
            TMP_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SRC_DB_PATH, TMP_DB_PATH)
        except Exception as e:
            print(f"Vercel DB setup warning: {e}")
    
    DEFAULT_DB_URI = f"sqlite:///{TMP_DB_PATH}" if TMP_DB_PATH.exists() else f"sqlite:///{SRC_DB_PATH}"
    DEFAULT_UPLOAD_FOLDER = str(Path('/tmp/uploads'))
    DEFAULT_LOG_PATH = str(Path('/tmp/logs/app.log'))
else:
    DEFAULT_DB_URI = f"sqlite:///{SRC_DB_PATH}"
    DEFAULT_UPLOAD_FOLDER = str(BASE_DIR / 'uploads')
    DEFAULT_LOG_PATH = str(BASE_DIR / 'logs' / 'app.log')

class Config:
    """Base Configuration Class containing common environment settings."""
    SECRET_KEY = get_env_str('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = get_env_str('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    
    # Storage & Files
    CSV_DATA_PATH = get_env_str('CSV_DATA_PATH', str(BASE_DIR / 'vendors_20_columns.csv'))
    UPLOAD_FOLDER = get_env_str('UPLOAD_FOLDER', DEFAULT_UPLOAD_FOLDER)
    MAX_CONTENT_LENGTH = get_int_env('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16 MB limit
    
    # Logging Configuration
    LOG_LEVEL = get_env_str('LOG_LEVEL', 'INFO').upper()
    LOG_FILE_PATH = get_env_str('LOG_FILE_PATH', DEFAULT_LOG_PATH)
    
    # AI/ML Configuration
    AI_MODEL_PATH = get_env_str('AI_MODEL_PATH', str(BASE_DIR / 'src' / 'infrastructure' / 'ml' / 'models'))
    AI_CONFIDENCE_THRESHOLD = get_float_env('AI_CONFIDENCE_THRESHOLD', 0.75)
    
    # Database Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = get_env_str('DATABASE_URL', DEFAULT_DB_URI)
    
    # Cache & Messaging Configuration
    REDIS_URL = get_env_str('REDIS_URL', 'redis://localhost:6379/0')
    
    # Security Configuration Default
    SECURITY_HEADERS_ENABLED = True
    CSRF_ENABLED = get_bool_env('CSRF_ENABLED', True)
    
    # Rate Limiting Configuration (Requests per Window in Seconds)
    RATE_LIMIT_LOGIN_COUNT = get_int_env('RATE_LIMIT_LOGIN_COUNT', 5)
    RATE_LIMIT_LOGIN_WINDOW = get_int_env('RATE_LIMIT_LOGIN_WINDOW', 60)
    
    RATE_LIMIT_SEARCH_COUNT = get_int_env('RATE_LIMIT_SEARCH_COUNT', 30)
    RATE_LIMIT_SEARCH_WINDOW = get_int_env('RATE_LIMIT_SEARCH_WINDOW', 60)
    
    RATE_LIMIT_AI_COUNT = get_int_env('RATE_LIMIT_AI_COUNT', 15)
    RATE_LIMIT_AI_WINDOW = get_int_env('RATE_LIMIT_AI_WINDOW', 60)
    
    RATE_LIMIT_UPLOAD_COUNT = get_int_env('RATE_LIMIT_UPLOAD_COUNT', 10)
    RATE_LIMIT_UPLOAD_WINDOW = get_int_env('RATE_LIMIT_UPLOAD_WINDOW', 60)

class DevelopmentConfig(Config):
    """Development Environment Settings."""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = get_env_str('LOG_LEVEL', 'DEBUG').upper()
    SQLALCHEMY_DATABASE_URI = get_env_str('DATABASE_URL', DEFAULT_DB_URI)

class TestingConfig(Config):
    """Testing Environment Settings."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_env_str('TEST_DATABASE_URL', 'sqlite:///:memory:')
    CSV_DATA_PATH = get_env_str('CSV_DATA_PATH_TEST', str(BASE_DIR / 'vendors_20_columns.csv'))
    SECURITY_HEADERS_ENABLED = False
    CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production Environment Settings."""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = get_env_str('LOG_LEVEL', 'WARNING').upper()
    SQLALCHEMY_DATABASE_URI = get_env_str('DATABASE_URL', DEFAULT_DB_URI)
    
    def __init__(self):
        super().__init__()
        # Fallback values if environment variables are not populated in Vercel/PaaS environment
        if not get_env_str('SECRET_KEY', '') and not IS_VERCEL:
            pass # Non-fatal fallback to inherited default

# Mapping of configurations to string identifiers
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Resolves and returns the active configuration class instance based on FLASK_ENV."""
    env = get_env_str('FLASK_ENV', 'development').lower()
    config_class = config_by_name.get(env, config_by_name['default'])
    return config_class()
