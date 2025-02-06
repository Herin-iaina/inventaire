import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """
    Dynamically generate database connection URL based on environment variables.
    Prioritizes full DATABASE_URL, then falls back to specific database configurations.
    """
    # Check for full DATABASE_URL first
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url

    # Fallback to database type selection
    db_type = os.getenv('DB_TYPE', 'postgresql').lower() # Default to PostgreSQL if not specified

    try:
        if db_type == 'mysql':
            db_config = {
                'user': os.getenv('MYSQL_USER', 'user'),
                'password': os.getenv('MYSQL_PASSWORD', 'password'),
                'host': os.getenv('MYSQL_HOST', 'localhost'),
                'database': os.getenv('MYSQL_DATABASE', 'macdb'),
                'port': os.getenv('MYSQL_PORT', '3306')
            }
            db_url = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}" # Use pymysql for MySQL

        elif db_type == 'postgresql': #Keep postgresql support
            db_config = {
                'user': os.getenv('POSTGRES_USER', 'user'),
                'password': os.getenv('POSTGRES_PASSWORD', 'password'),
                'host': os.getenv('POSTGRES_HOST', 'localhost'),
                'database': os.getenv('POSTGRES_DATABASE', 'macdb'),
                'port': os.getenv('POSTGRES_PORT', '5432')
            }
            db_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

        else:
            raise ValueError(f"Unsupported database type: {db_type}. Use 'mysql' or 'postgresql'.")

        return db_url

    except KeyError as e:
        logger.error(f"Missing database configuration: {e}")
        raise

def create_database_engine(db_url=None):
    """
    Create and test database engine with connection pooling and error handling.
    """
    if not db_url:
        db_url = get_database_url()

    try:
        # Additional connection parameters for robustness
        engine = create_engine(
            db_url,
            pool_size=10,  # Adjust based on expected concurrent connections
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1800,  # Recycle connections every 30 minutes
            pool_pre_ping=True  # Test connection before using
        )

        # Verify connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        logger.info("Database connection successfully established!")
        return engine

    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        raise

# Create base and session factory
Base = declarative_base()
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency for getting database session in FastAPI.
    Ensures proper session management and closure.
    """
    db = SessionLocal()
    try:
        yield db
        return db
    finally:
        db.close()
        return False