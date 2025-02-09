from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.gocardless_service import fetch_gocardless_transactions
from utils.security import get_current_user
from database import get_db

router = APIRouter()

@router.get("/transactions/")
def get_gocardless_transactions(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Fetch transactions from GoCardless API using the linked account ID."""
    try:
        return fetch_gocardless_transactions(db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
