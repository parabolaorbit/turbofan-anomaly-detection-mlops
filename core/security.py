from fastapi import Header, HTTPException, status
from core.config import settings

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            content={
                "error_code": "INVALID_API_KEY",
                "message": "Invalid API key",
                "status_code": 401,
            },
        )