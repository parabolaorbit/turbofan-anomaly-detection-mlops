#========================================================
# APIキー認証を行う関数
#========================================================
from fastapi import Header, HTTPException
from core.config import settings

def verify_api_key(x_api_key: str = Header(...)):
    """APIキー認証を行う関数"""
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            content={
                "error_code": "INVALID_API_KEY",
                "message": "Invalid API key",
                "status_code": 401,
            },
        )