from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Get Database URL from environtment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True # set false in production, True untuk debugging
)

#create sessionlocal clas
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base Class For Models
Base = declarative_base()

#depedency untuk mendapatkan database session
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()