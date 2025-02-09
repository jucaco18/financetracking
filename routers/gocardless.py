from fastapi import APIRouter, Depends
from services.nordigen_service import get_bank_transactions

router = APIRouter()

@router.get("/gocardless/transactions/{account_id}")
def fetch_transactions(account_id: str):
    """
    Fetch bank transactions from GoCardless.
    """
    transactions = get_bank_transactions(account_id)
    return transactions if transactions else {"error": "Failed to fetch transactions"}
