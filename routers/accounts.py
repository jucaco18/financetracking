from fastapi import APIRouter

router = APIRouter()

@router.get("/test-accounts")
def test_accounts():
    return {"message": "Accounts API is working!"}
