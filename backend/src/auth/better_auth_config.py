"""Better Auth configuration for the Todo Evolution application."""

from datetime import timedelta
from typing import Dict, Any, List
from src.core.config import settings
from src.models.models import User


# Simplified auth configuration for JWT tokens
# Note: Better Auth integration is simplified for current MVP


# Helper functions for JWT token management
def create_access_token(user_id: int, email: str) -> str:
    """
    Create JWT access token.

    Args:
        user_id: User ID
        email: User email

    Returns:
        str: JWT access token
    """
    from jose import jwt
    from datetime import datetime, timedelta

    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }

    return jwt.encode(
        payload,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(user_id: int) -> str:
    """
    Create JWT refresh token.

    Args:
        user_id: User ID

    Returns:
        str: JWT refresh token
    """
    from jose import jwt
    from datetime import datetime, timedelta

    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }

    return jwt.encode(
        payload,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verify JWT token and return payload.

    Args:
        token: JWT token to verify
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Dict[str, Any]: Token payload

    Raises:
        ValueError: If token is invalid
    """
    from jose import jwt, JWTError
    from datetime import datetime

    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Check token type
        if payload.get("type") != token_type:
            raise ValueError(f"Invalid token type. Expected {token_type}")

        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise ValueError("Token has expired")

        return payload

    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")


