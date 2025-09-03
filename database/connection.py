from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from config import Config

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database for the application"""
        # Create data directory if it doesn't exist
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        
        # SQLite database for application metadata
        database_url = f"sqlite:///{os.path.join(Config.DATA_DIR, 'data_retrieval.db')}"
        
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def create_tables(self):
        """Create all database tables"""
        from .models import Base
        Base.metadata.create_all(bind=self.engine)
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()

# Global database manager instance
db_manager = DatabaseManager()

def get_db():
    """Dependency to get database session"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()
