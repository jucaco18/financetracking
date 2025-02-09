import pandas as pd
from sqlalchemy.orm import Session
from models import Transaction, HistoricalCategorization

# Load Budget Type mapping
budget_df = pd.read_csv("Budget Type.csv")
budget_map = {row["category"]: row["budget_type"] for _, row in budget_df.iterrows()}  # { Category: Budget Type }

# Load Account Ownership mapping
account_df = pd.read_csv("Account Map.csv")
account_map = {row["iban"]: row["name"] for _, row in account_df.iterrows()}  # { IBAN: Account Name }

def categorize_transactions(db: Session):
    """Applies categorization logic based on historical data and predefined budget mappings."""
    transactions = db.query(Transaction).filter(Transaction.categorized == False).all()

    for txn in transactions:
        category = "Uncategorized"
        budget_type = "Uncategorized"
        author = "Unknown"

        # Fetch historical categorization
        historical_match = db.query(HistoricalCategorization).filter(
            (HistoricalCategorization.creditor_name == txn.creditor_name) |
            (HistoricalCategorization.creditor_iban == txn.creditor_iban) |
            (HistoricalCategorization.debtor_name == txn.debtor_name) |
            (HistoricalCategorization.debtor_iban == txn.debtor_iban) |
            (HistoricalCategorization.additional_info.like(f"%{txn.remittance_info}%"))
        ).first()

        if historical_match:
            category = historical_match.category
            budget_type = historical_match.budget_type
        else:
            # Match category using budget_map based on creditor name
            for keyword, mapped_budget_type in budget_map.items():
                if keyword.lower() in txn.creditor_name.lower():
                    category = keyword
                    budget_type = mapped_budget_type
                    break

        # Determine author based on shared expenses
        account_name = account_map.get(txn.account_iban, "Unknown")
        if budget_type == "Shared Expense":
            author = "Shared"
        else:
            author = account_name  # Assign based on account ownership

        # Update the transaction
        txn.category = category
        txn.budget_type = budget_type
        txn.categorized = True
        txn.author = author

    db.commit()
