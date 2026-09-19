import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=True)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

JWT_ISSUER = os.getenv("JWT_ISSUER", "secure-rest-api")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "secure-rest-api-client")


if not JWT_SECRET_KEY:
    raise RuntimeError(
        f"JWT_SECRET_KEY is missing. Expected .env file at: {ENV_FILE}"
    )