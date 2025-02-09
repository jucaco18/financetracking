from uuid import uuid4
from nordigen import NordigenClient
from dotenv import load_dotenv
import os
import requests
from sqlalchemy.orm import Session
from models import Transaction

# Load credentials from environment variables
load_dotenv()
GOCARDLESS_ACCESS_TOKEN = os.getenv("GOCARDLESS_ACCESS_TOKEN")
GOCARDLESS_REFRESH_TOKEN = os.getenv("GOCARDLESS_REFRESH_TOKEN")
GOCARDLESS_CLIENT_ID = os.getenv("GOCARDLESS_CLIENT_ID")
GOCARDLESS_SECRET_ID = os.getenv("GOCARDLESS_SECRET_ID")
GOCARDLESS_ACCOUNT_ID = os.getenv("GOCARDLESS_ACCOUNT_ID")


#Fetch transactions from GoCardless API

GOCARDLESS_API_BASE_URL = "https://bankaccountdata.gocardless.com/api/v2"

def fetch_gocardless_transactions(db: Session):
    """Fetch transactions from GoCardless API using the linked account ID."""
    if not GOCARDLESS_ACCOUNT_ID:
        raise ValueError("GoCardless Account ID is missing. Ensure it is set in the .env file.")

    url = f"{GOCARDLESS_API_BASE_URL}/accounts/{GOCARDLESS_ACCOUNT_ID}/transactions"
    headers = {"Authorization": f"Bearer {GOCARDLESS_ACCESS_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"GoCardless API Error: {response.text}")

    transactions = response.json().get("transactions", {}).get("booked", [])

    batch_data = []
    for txn in transactions:
        transaction_id = txn.get("internalTransactionId", txn.get("transactionId", ""))
        existing_txn = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
        if existing_txn:
            continue  # Skip duplicate transactions

        batch_data.append(Transaction(
            date=txn["bookingDate"],
            amount=float(txn["transactionAmount"]["amount"]),
            description=txn.get("remittanceInformationUnstructured", "No Description"),
            category="Uncategorized",
            transaction_id=transaction_id
        ))

    db.bulk_save_objects(batch_data)
    db.commit()
    return {"message": "Transactions synced successfully", "total": len(batch_data)}
