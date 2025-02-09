from sqlalchemy import Column, Integer, String, Float, Date, Boolean, UniqueConstraint
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, default="Uncategorized")
    manually_reviewed = Column(Boolean, default=False)
    transaction_id = Column(String, unique=True, nullable=True)

    __table_args__ = (UniqueConstraint("transaction_id", name="unique_transaction"),)

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
    is_shared_expense = Column(Boolean, nullable=False)

class SyncLog(Base):
    __tablename__ = "sync_log"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Date, nullable=False)
    event_type = Column(String, nullable=False)
    details = Column(String, nullable=False)
