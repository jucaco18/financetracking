from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import engine, SessionLocal, init_db
from models import User, Transaction, HistoricalCategorization, BudgetType, SyncLog
import schemas
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv
import os
from services.categorization import categorize_transactions
from routers import transactions, gocardless, authentication, crypto, accounts

# Load .env file
load_dotenv()

app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(gocardless.router, prefix="/gocardless", tags=["GoCardless"])
app.include_router(authentication.router, prefix="/auth", tags=["Authentication"])
app.include_router(crypto.router, prefix="/crypto", tags=["Crypto"])
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])


# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1

def get_db():
    """Dependency to get the database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str):
    """Hashes a password securely."""
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """Verifies a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)):
    """Generates a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)):
    """Extracts the current user from the JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# User Registration Endpoint
@app.post("/register/", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Registers a new user."""
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, password_hash=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# User Login Endpoint
from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login/")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}


# Create Transaction Endpoint with Categorization
@app.post("/transactions/", response_model=schemas.TransactionResponse)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new transaction with automatic categorization."""
    category, budget_type = categorize_transaction(
        db,
        transaction.description,
        transaction.description,
        transaction.description,
        transaction.description,
        transaction.description
    )

    new_transaction = Transaction(
        date=transaction.date,
        amount=transaction.amount,
        description=transaction.description,
        category=category
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction

# Retrieve All Transactions Endpoint
@app.get("/transactions/", response_model=list[schemas.TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves all transactions for the authenticated user."""
    return db.query(Transaction).all()

@app.put("/transactions/{transaction_id}/categorize/")
def manually_categorize_transaction(
    transaction_id: int,
    new_category: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Allows users to manually update a transaction's category."""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction.category = new_category
    transaction.manually_reviewed = True  # Mark as manually categorized
    db.commit()

    return {"message": "Transaction updated successfully", "transaction_id": transaction.id, "new_category": new_category}
