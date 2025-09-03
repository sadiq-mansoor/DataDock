import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configurations
    DATABASE_CONFIGS = {
        'postgres': {
            'driver': 'postgresql',
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'data_retrieval'),
            'username': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'password')
        },
        'mysql': {
            'driver': 'mysql+pymysql',
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': os.getenv('MYSQL_PORT', '3306'),
            'database': os.getenv('MYSQL_DB', 'data_retrieval'),
            'username': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', 'password')
        }
    }
    
    # File paths
    DATA_DIR = 'data'
    LOGS_DIR = 'logs'
    EXPORTS_DIR = 'exports'
    SCHEMAS_DIR = 'schemas'
    
    # Security settings
    SENSITIVE_FIELDS = [
        'password', 'ssn', 'credit_card', 'phone', 'email',
        'address', 'salary', 'medical_record', 'bank_account'
    ]
    
    # User roles
    ROLES = {
        'super_admin': 'Super Admin',
        'admin': 'Admin', 
        'user': 'User'
    }
    
    # Audit log settings
    AUDIT_LOG_FILE = os.path.join(LOGS_DIR, 'audit.log')
    
    @classmethod
    def get_database_url(cls, db_type, **kwargs):
        """Generate database URL for SQLAlchemy"""
        config = cls.DATABASE_CONFIGS.get(db_type, {}).copy()
        config.update(kwargs)
        
        if db_type == 'postgres':
            return f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        elif db_type == 'mysql':
            return f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        else:
            return None
