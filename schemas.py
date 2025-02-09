from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class TransactionCreate(BaseModel):
    account_name: Optional[str]
    account_iban: Optional[str]
    transaction_id: Optional[str]  # ✅ Added
    date: date
    amount: float
    currency: Optional[str] = "EUR"
    creditor_name: Optional[str]
    creditor_iban: Optional[str]
    debtor_name: Optional[str]
    debtor_iban: Optional[str]
    additional_information: Optional[str]
    category: Optional[str] = "Uncategorized"
    budget_type: Optional[str] = "Uncategorized"
    categorized: Optional[bool] = False  # ✅ Added
    manual_flag: Optional[bool] = False  # ✅ Added
    author: Optional[str]
    manually_reviewed: Optional[bool] = False
    month: Optional[str]  # ✅ Added (Extracted from date)
    year: Optional[str]  # ✅ Added (Extracted from date)


class TransactionResponse(TransactionCreate):
    id: int
    category: str

    class Config:
        form_attributes = True


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        form_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str
