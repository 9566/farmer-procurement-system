"""
Authentication utilities.

Features:
- Password hashing
- Password verification
- JWT creation
- JWT decoding
- Current-user authentication
- Role-based authorization
"""

import os

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt

from passlib.context import CryptContext


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")
load_dotenv()


# ============================================================
# JWT CONFIGURATION
# ============================================================

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is missing. Add SECRET_KEY to your .env file."
    )


ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)


ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "480"
    )
)


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ============================================================
# OAUTH2
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(password: str) -> str:

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    try:

        return pwd_context.verify(
            plain_password,
            hashed_password
        )

    except Exception:

        return False


# ============================================================
# CREATE TOKEN
# ============================================================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:

    payload = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + (
            expires_delta
            or timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )
    )

    payload.update(
        {
            "exp": expire
        }
    )

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ============================================================
# DECODE TOKEN
# ============================================================

def decode_token(token: str) -> dict:

    try:

        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )


# ============================================================
# CURRENT USER
# ============================================================

def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> dict:

    payload = decode_token(token)

    sub = payload.get("sub")

    role = payload.get("role")

    if sub is None or role is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    try:

        user_id = int(sub)

    except (TypeError, ValueError):

        raise HTTPException(
            status_code=401,
            detail="Invalid user ID in token"
        )

    return {
        "user_id": user_id,
        "role": role,
        "centre_id": payload.get("centre_id"),
    }


# ============================================================
# ROLE CHECK
# ============================================================

def require_role(*allowed_roles: str):

    def checker(
        payload: dict = Depends(get_current_user)
    ) -> dict:

        if payload.get("role") not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource"
            )

        return payload

    return checker