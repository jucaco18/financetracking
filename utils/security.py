from fastapi import Depends, HTTPException, Security
from sqlalchemy.orm import Session
from database import get_db
from models import User
import jwt
from fastapi.security import OAuth2PasswordBearer
import os
from jwt import PyJWTError
from dotenv import load_dotenv

load_dotenv()  # ✅ Load environment variables

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey").strip()  # ✅ Ensuring it's a valid string
ALGORITHM = "HS256"

def get_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)):
    """Extracts the current user from JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user  # ✅ Now returning a `User` object
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
