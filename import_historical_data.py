import csv
from sqlalchemy.orm import Session
from database import SessionLocal, HistoricalCategorization

# Define the CSV file path
CSV_FILE_PATH = "historical_categorization.csv"

def import_categorization_data():
    db: Session = SessionLocal()
    try:
        with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row

            for row in reader:
                creditor_name = row[0]
                creditor_iban = row[1]
                debtor_name = row[2]
                debtor_iban = row[3]
                additional_info = row[4]
                category = row[5]
                budget_type = row[6]

                # Check if entry already exists
                existing_entry = db.query(HistoricalCategorization).filter(
                    HistoricalCategorization.creditor_name == creditor_name,
                    HistoricalCategorization.creditor_iban == creditor_iban,
                    HistoricalCategorization.debtor_name == debtor_name,
                    HistoricalCategorization.debtor_iban == debtor_iban,
                    HistoricalCategorization.additional_info == additional_info
                ).first()

                if not existing_entry:
                    new_entry = HistoricalCategorization(
                        creditor_name=creditor_name,
                        creditor_iban=creditor_iban,
                        debtor_name=debtor_name,
                        debtor_iban=debtor_iban,
                        additional_info=additional_info,
                        category=category,
                        budget_type=budget_type
                    )
                    db.add(new_entry)

            db.commit()
            print("✅ Historical categorization data imported successfully.")
    except Exception as e:
        print(f"❌ Error importing data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_categorization_data()
