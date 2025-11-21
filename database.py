from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Create Database URL
SQLALCHEMY_DATABASE_URL = "postgresql://ryleymao@localhost/todo_api"

# Engine manages actual connection to PostgreSQL "translater" between Python and database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Conversation with database (bind connects, autocommit controls when to save changes, autoflush controls when to save)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creates a new database session (yield gives it to endpoint to use, 
# finally ensures connection closes even with error prevents connection leaks)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()