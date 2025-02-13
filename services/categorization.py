import pandas as pd
from sqlalchemy.orm import Session
from models import HistoricalCategorization

# Load Budget Type mapping
budget_df = pd.read_csv("Budget Type.csv")
budget_map = {row["Category"]: row["Budget Type"] for _, row in budget_df.iterrows()}  # { Category: Budget Type }

# Load Account Ownership mapping
account_df = pd.read_csv("Account Map.csv")
account_map = {row["IBAN"]: row["Account Name"] for _, row in account_df.iterrows()}  # { IBAN: Account Name }

# Load Shared Expense mapping
shared_expense_map = {row["Category"]: row["Shared expense"] for _, row in budget_df.iterrows()}  # { Category: Shared Expense }

def categorize_transactions(
    db: Session,
    account_name: str,
    account_iban: str,
    creditor_name: str,
    creditor_iban: str,
    debtor_iban: str,
    additional_information: str,
    amount: float  # Needed to determine Transfer In/Out
) -> (str, str, str):
    """Categorizes a transaction and returns (category, budget_type, author)."""

    category = "Uncategorized"
    budget_type = "Uncategorized"
    author = "Unknown"

    print(f"🔍 Processing Transaction:")
    print(f"  - Account Name: {account_name}")
    print(f"  - Creditor Name: {creditor_name}")
    print(f"  - Creditor IBAN: {creditor_iban}")
    print(f"  - Debtor IBAN: {debtor_iban}")
    print(f"  - Additional Info: {additional_information}")
    print(f"  - Amount: {amount}")

    # ✅ **Special Case: American Express - Transfer In**
    if account_name == "American Express" and creditor_name == "HARTELIJK BEDANKT VOOR UW BETALING":
        category = "Transfer In"
        budget_type = "Internal Transfer"
        print("✅ Categorized as Special Case: American Express Transfer In")
    
    # ✅ **Special Case: Internal Transfer (Both IBANs belong to user)**
    elif creditor_iban in account_map and debtor_iban in account_map:
        category = "Transfer In" if amount > 0 else "Transfer Out"
        budget_type = "Internal Transfer"
        print("✅ Categorized as Internal Transfer")

    else:
        # 1️⃣ **Match by Creditor Name / Debtor Name**
        historical_match = db.query(HistoricalCategorization).filter(
            (HistoricalCategorization.creditor_name == creditor_name) |
            (HistoricalCategorization.debtor_name == creditor_name)  # Match debtor for income
        ).first()

        if historical_match:
            category = historical_match.category
            budget_type = historical_match.budget_type
            print(f"✅ Matched by Creditor/Debtor Name: {category}, {budget_type}")

        else:
            # 2️⃣ **Match by Additional Information**
            historical_match = db.query(HistoricalCategorization).filter(
                HistoricalCategorization.additional_info.like(f"%{additional_information}%")  # Partial match
            ).first()

            if historical_match:
                category = historical_match.category
                budget_type = historical_match.budget_type
                print(f"✅ Matched by Additional Information: {category}, {budget_type}")

            else:
                # 3️⃣ **Match by Creditor IBAN / Debtor IBAN**
                historical_match = db.query(HistoricalCategorization).filter(
                    (HistoricalCategorization.creditor_iban == creditor_iban) |
                    (HistoricalCategorization.debtor_iban == debtor_iban)
                ).first()

                if historical_match:
                    category = historical_match.category
                    budget_type = historical_match.budget_type
                    print(f"✅ Matched by Creditor/Debtor IBAN: {category}, {budget_type}")

    # ✅ **Determine `author` (Based on Shared Expense or Account Ownership)**
    if shared_expense_map.get(category) == "Yes":
        author = "Shared"
    else:
        author = account_map.get(account_iban, "Unknown")

    print(f"🔹 Final Categorization → Category: {category}, Budget Type: {budget_type}, Author: {author}")

    return category, budget_type, author
