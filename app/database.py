from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from app.config import settings
from app.models import Base
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session: # type: ignore
    """
    Dependency function to get database session
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """
    Initialize database tables
    """
    try:
        Base.metadata.drop_all(bind=engine)  # Added this line to drop all tables first
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
        
        # Reset sequences after table creation
        reset_sequences()
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def reset_sequences():
    """
    Reset PostgreSQL sequences to start from 1
    """
    try:
        with engine.connect() as conn:
            # Reset tools table sequence
            conn.execute(text("ALTER SEQUENCE tools_id_seq RESTART WITH 1"))
            # Reset search_history table sequence
            conn.execute(text("ALTER SEQUENCE search_history_id_seq RESTART WITH 1"))
            conn.commit()
        logger.info("Database sequences reset successfully!")
    except Exception as e:
        logger.error(f"Error resetting sequences: {e}")