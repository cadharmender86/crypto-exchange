from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from app.core.config import settings
password_hash = PasswordHash.recommended()

ALGORITHM = "H256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str,) -> bool:
    return password_hash.verify(plain_password,hashed_password,)

def create_access_token(user_id: UUID) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": "access",
        "exp": expires,
    }

    return jwt.encode(payload, settings.jwt_secret_key,algorithm=ALGORITHM,)

def create_refresh_token(user_id: UUID) -> str:
    expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": "access",
        "exp": expires,
    }
    return jwt.encode(payload, settings.jwt_secret_key,algorithm=ALGORITHM,)