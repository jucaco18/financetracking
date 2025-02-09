from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, UniqueConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
Base = declarative_base()

# Create a database engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency function to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db  # Give the database session to the request
    finally:
        db.close()  # Close session after request

def init_db():
    Base.metadata.create_all(bind=engine)
