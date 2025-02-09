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
    amount: float  # Added amount to determine Transfer In/Out
) -> (str, str, str):
    """Categorizes a transaction and returns (category, budget_type, author)."""

    category = "Uncategorized"
    budget_type = "Uncategorized"
    author = "Unknown"

    # ✅ **Special Case: American Express - Transfer In**
    if account_name == "American Express" and creditor_name == "HARTELIJK BEDANKT VOOR UW BETALING":
        category = "Transfer In"
        budget_type = "Internal Transfer"

    # ✅ **Special Case: Internal Transfer (Both IBANs belong to user)**
    elif creditor_iban in account_map and debtor_iban in account_map:
        category = "Transfer In" if amount > 0 else "Transfer Out"
        budget_type = "Internal Transfer"

    else:
        # ✅ **Check against historical categorization**
        historical_match = db.query(HistoricalCategorization).filter(
            (HistoricalCategorization.creditor_name == creditor_name) |
            (HistoricalCategorization.creditor_iban == creditor_iban) |
            (HistoricalCategorization.debtor_iban == debtor_iban) |
            (HistoricalCategorization.additional_info.like(f"%{additional_information}%"))  # Allow partial match
        ).first()

        if historical_match:
            category = historical_match.category
            budget_type = historical_match.budget_type
        else:
            # ✅ **Match by Creditor Name / Debtor Name**
            for keyword, mapped_budget_type in budget_map.items():
                if creditor_name and keyword.lower() in creditor_name.lower():
                    category = keyword
                    budget_type = mapped_budget_type
                    break

            # ✅ **Match by Additional Information (If not matched already)**
            if category == "Uncategorized":
                for keyword, mapped_budget_type in budget_map.items():
                    if additional_information and keyword.lower() in additional_information.lower():
                        category = keyword
                        budget_type = mapped_budget_type
                        break

            # ✅ **Match by Creditor IBAN / Debtor IBAN (If still not matched)**
            if category == "Uncategorized":
                for keyword, mapped_budget_type in budget_map.items():
                    if creditor_iban and keyword.lower() in creditor_iban.lower():
                        category = keyword
                        budget_type = mapped_budget_type
                        break
                    if debtor_iban and keyword.lower() in debtor_iban.lower():
                        category = keyword
                        budget_type = mapped_budget_type
                        break

    # ✅ **Determine `author` (Based on Shared Expense or Account Ownership)**
    if shared_expense_map.get(category) == "Yes":
        author = "Shared"
    else:
        author = account_map.get(account_iban, "Unknown")

    return category, budget_type, author
