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

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    amount = Column(Float)
    description = Column(String)
    category = Column(String, default="Uncategorized")
    manually_reviewed = Column(Boolean, default=False)
    transaction_id = Column(String, unique=True)


class HistoricalCategorization(Base):
    __tablename__ = "historical_categorization"
    id = Column(Integer, primary_key=True, index=True)
    creditor_name = Column(String)
    creditor_iban = Column(String)
    debtor_name = Column(String)
    debtor_iban = Column(String)
    additional_info = Column(String)
    category = Column(String)
    budget_type = Column(String)

class BudgetType(Base):
    __tablename__ = "budget_type"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, unique=True, nullable=False)
    is_shared_expense = Column(String, nullable=False)  # "Yes" or "No"

class SyncLog(Base):
    __tablename__ = "sync_log"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Date, default=datetime.utcnow)
    event_type = Column(String, nullable=False)
    details = Column(String, nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)
