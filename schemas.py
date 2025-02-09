from pydantic import BaseModel
from datetime import date

class TransactionCreate(BaseModel):
    date: date
    amount: float
    description: str

class TransactionResponse(TransactionCreate):
    id: int
    category: str

    class Config:
        form_attributes = True

from pydantic import BaseModel, EmailStr

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
