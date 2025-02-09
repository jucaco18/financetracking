from fastapi import APIRouter

router = APIRouter()

@router.get("/test-crypto")
def test_crypto():
    return {"message": "Crypto API is working!"}
