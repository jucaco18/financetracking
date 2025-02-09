from uuid import uuid4
from nordigen import NordigenClient
import os
from dotenv import load_dotenv

# Load credentials from environment variables
load_dotenv()
NORDIGEN_SECRET_ID = os.getenv("NORDIGEN_SECRET_ID")
NORDIGEN_SECRET_KEY = os.getenv("NORDIGEN_SECRET_KEY")

# Initialize Nordigen client
client = NordigenClient(secret_id=NORDIGEN_SECRET_ID, secret_key=NORDIGEN_SECRET_KEY)

# Authenticate (Fetch access token)
token_data = client.generate_token()

# Function to initialize a bank session
def initialize_bank_session(country, institution_name, redirect_uri):
    institution_id = client.institution.get_institution_id_by_name(
        country=country,
        institution=institution_name
    )
    init = client.initialize_session(
        institution_id=institution_id,
        redirect_uri=redirect_uri,
        reference_id=str(uuid4())
    )
    return init.link, init.requisition_id

# Function to fetch account transactions
def get_bank_transactions(requisition_id):
    accounts = client.requisition.get_requisition_by_id(requisition_id=requisition_id)
    account_id = accounts["accounts"][0]
    account = client.account_api(id=account_id)
    transactions = account.get_transactions()
    return transactions

# Function to fetch account details
def get_account_details(requisition_id):
    accounts = client.requisition.get_requisition_by_id(requisition_id=requisition_id)
    account_id = accounts["accounts"][0]
    account = client.account_api(id=account_id)
    details = account.get_details()
    return details

# Function to fetch account balances
def get_account_balances(requisition_id):
    accounts = client.requisition.get_requisition_by_id(requisition_id=requisition_id)
    account_id = accounts["accounts"][0]
    account = client.account_api(id=account_id)
    balances = account.get_balances()
    return balances