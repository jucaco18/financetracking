import requests
import os
from sqlalchemy.orm import Session
from models import Transaction
from datetime import datetime
import pandas as pd

GOCARDLESS_API_BASE_URL = "https://bankaccountdata.gocardless.com/api/v2"
GOCARDLESS_ACCESS_TOKEN = os.getenv("GOCARDLESS_ACCESS_TOKEN")
GOCARDLESS_ACCOUNT_ID = os.getenv("GOCARDLESS_ACCOUNT_ID")

# Load account mapping
account_map_df = pd.read_csv("Account Map.csv")
account_map = {row["iban"]: row["name"] for _, row in account_map_df.iterrows()}  # { IBAN: Account Name }

def fetch_gocardless_transactions(db: Session):
    """Fetch transactions from GoCardless API and store them in standardized format."""
    url = f"{GOCARDLESS_API_BASE_URL}/accounts/{GOCARDLESS_ACCOUNT_ID}/transactions"
    headers = {"Authorization": f"Bearer {GOCARDLESS_ACCESS_TOKEN}"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"GoCardless API Error: {response.text}")

    data = response.json()
    transactions = data.get("transactions", {}).get("booked", [])

    standardized_transactions = []

    for txn in transactions:
        account_iban = txn["debtorAccount"]["iban"] if "debtorAccount" in txn else "Unknown"
        account_name = account_map.get(account_iban, "Unknown")

        standardized_transactions.append(Transaction(
            transaction_id=txn.get("transactionId"),
            date=datetime.strptime(txn.get("bookingDate"), "%Y-%m-%d").date(),
            amount=float(txn["transactionAmount"]["amount"]),
            currency=txn["transactionAmount"]["currency"],
            account_name=account_name,
            account_iban=account_iban,
            creditor_name=txn.get("creditorName", "N/A"),
            creditor_iban=txn.get("creditorAccount", {}).get("iban", "N/A"),
            debtor_name=txn.get("debtorName", "N/A"),
            debtor_iban=txn.get("debtorAccount", {}).get("iban", "N/A"),
            remittance_info=txn.get("remittanceInformationUnstructured", "N/A"),
            additional_information=txn.get("additionalInformation", "N/A"),
            bank_transaction_code=txn.get("bankTransactionCode", "N/A"),
            month=datetime.strptime(txn.get("bookingDate"), "%Y-%m-%d").strftime("%B"),
            year=datetime.strptime(txn.get("bookingDate"), "%Y-%m-%d").strftime("%Y"),
            categorized=False,
            manual_flag=False,
            manually_reviewed=False
        ))

    db.bulk_save_objects(standardized_transactions)
    db.commit()

    return {"message": "Transactions synced successfully", "total": len(standardized_transactions)}