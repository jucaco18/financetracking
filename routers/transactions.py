from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Transaction
import schemas
from services.categorization import categorize_transaction
from utils.security import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.TransactionResponse, operation_id="create_transaction_main")
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Creates a new transaction with automatic categorization."""
    category, _ = categorize_transaction(db, transaction.description, "", "", "", "")

    new_transaction = Transaction(
        date=transaction.date,
        amount=transaction.amount,
        description=transaction.description,
        category=category
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction

@router.get("/", response_model=list[schemas.TransactionResponse], operation_id="get_transactions_main")
def get_transactions(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Retrieves all transactions for the authenticated user."""
    return db.query(Transaction).all()
