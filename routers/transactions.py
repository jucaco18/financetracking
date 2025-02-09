from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Transaction, User
import schemas
from services.categorization import categorize_transactions
from utils.security import get_current_user
from typing import Optional

router = APIRouter()

@router.post("/", response_model=schemas.TransactionResponse, operation_id="create_transaction_main")
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new transaction with automatic categorization."""
    

    # Perform automatic categorization
    category, budget_type, author = categorize_transactions(
        db,
        transaction.account_name,
        transaction.account_iban,
        transaction.creditor_name,
        transaction.creditor_iban,
        transaction.debtor_iban,
        transaction.additional_information,
        transaction.amount
    )

    new_transaction = Transaction(
        account_name=transaction.account_name,
        account_iban=transaction.account_iban,
        transaction_id=transaction.transaction_id,
        date=transaction.date,
        amount=transaction.amount,
        currency=transaction.currency,
        creditor_name=transaction.creditor_name,
        creditor_iban=transaction.creditor_iban,
        debtor_name=transaction.debtor_name,
        debtor_iban=transaction.debtor_iban,
        additional_information=transaction.additional_information,
        category=category,
        budget_type=budget_type,
        categorized=True,
        manual_flag=False,
        author=author,
        manually_reviewed=False,
        month=transaction.date.strftime("%B"),
        year=transaction.date.strftime("%Y")
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction


@router.get("/", response_model=list[schemas.TransactionResponse], operation_id="get_transactions_main")
def get_transactions(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Retrieves all transactions for the authenticated user."""
    return db.query(Transaction).all()

@router.delete("/transactions/")
def delete_all_transactions(db: Session = Depends(get_db)):
    """Delete all transactions from the database."""
    try:
        db.query(Transaction).delete()
        db.commit()
        return {"message": "All transactions deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
