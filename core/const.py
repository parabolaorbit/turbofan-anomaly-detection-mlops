FASTAPI_PREDICTION_RESPONSE = {
    401: {
        "description": "Invalid API key",
        "content": {
            "application/json": {
                "example": {
                    "error_code": "INVALID_API_KEY",
                    "message": "Invalid API key",
                    "status_code": 401,
                }
            }
        },
    },
    429: {
        "description": "Rate limit exceeded",
        "content": {
            "application/json": {
                "example": {
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": "Rate limit exceeded",
                    "status_code": 429,
                }
            }
        },
    },
}

FASTAPI_PREDICTION_DESCRIPTION = (
    "Receives turbofan sensor sequence data and returns reconstruction error, anomaly result, and model metadata."
)