from sqlalchemy.orm import Session
from database import HistoricalCategorization

def categorize_transaction(db: Session, creditor_name: str, creditor_iban: str, debtor_name: str, debtor_iban: str, additional_info: str) -> tuple:
    # Convert inputs to lowercase
    creditor_name = creditor_name.lower() if creditor_name else ""
    debtor_name = debtor_name.lower() if debtor_name else ""
    additional_info = additional_info.lower() if additional_info else ""

    # Retrieve historical categorization rules from DB
    history_rules = db.query(HistoricalCategorization).all()

    for rule in history_rules:
        if rule.creditor_name and rule.creditor_name.lower() == creditor_name:
            return rule.category, rule.budget_type
        if rule.debtor_name and rule.debtor_name.lower() == debtor_name:
            return rule.category, rule.budget_type
        if rule.creditor_iban and rule.creditor_iban == creditor_iban:
            return rule.category, rule.budget_type
        if rule.debtor_iban and rule.debtor_iban == debtor_iban:
            return rule.category, rule.budget_type
        if rule.additional_info and rule.additional_info.lower() in additional_info:
            return rule.category, rule.budget_type

    return "Uncategorized", "Uncategorized"
