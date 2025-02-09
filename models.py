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
    transaction_id = Column(String, unique=True, index=True)
    date = Column(Date)
    amount = Column(Float)
    currency = Column(String, default="EUR")
    account_name = Column(String)  # NEW: Derived from Account Map
    account_iban = Column(String)  # NEW: Derived from Account Map
    creditor_name = Column(String, nullable=True)
    creditor_iban = Column(String, nullable=True)
    debtor_name = Column(String, nullable=True)
    debtor_iban = Column(String, nullable=True)
    remittance_info = Column(String, nullable=True)
    additional_information = Column(String, nullable=True)  # NEW: Matches 'remittanceInformationUnstructured'
    bank_transaction_code = Column(String, nullable=True)
    category = Column(String, nullable=True)  # NEW: Categorized field
    budget_type = Column(String, nullable=True)  # NEW: Categorization linked field
    categorized = Column(Boolean, default=False)  # NEW: Boolean to track if categorized
    manual_flag = Column(Boolean, default=False)  # NEW: Boolean for manual review
    author = Column(String, nullable=True)  # NEW: Owner based on account
    manually_reviewed = Column(Boolean, default=False)  # NEW: Indicates manual review completion
    month = Column(String)  # NEW: Extracted from date
    year = Column(String)  # NEW: Extracted from date


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
