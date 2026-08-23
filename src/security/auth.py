import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


load_dotenv(override=True)

security = HTTPBearer()

API_TOKEN = os.getenv("API_TOKEN")


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    return credentials.credentials