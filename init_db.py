from app.database import init_db, engine
from app.config import settings
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_sequences():
    """Reset PostgreSQL sequences to start from 1"""
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

if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db()
    reset_sequences()
    logger.info("Database initialization complete!")