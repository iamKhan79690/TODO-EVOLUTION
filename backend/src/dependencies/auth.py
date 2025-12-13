"""Authentication dependencies for JWT token validation."""

from typing import Optional
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.core.database import get_session_dependency
from src.models.models import User
from src.auth.token_store import token_blacklist

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session_dependency())
) -> User:
    """
    Validate JWT token and return current user.

    Args:
        credentials: HTTP Bearer credentials
        session: Database session

    Returns:
        User: Authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        # Check if token is blacklisted
        is_blacklisted = await token_blacklist.is_blacklisted(token)
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id_str = payload.get("sub")
        user_id: int = int(user_id_str) if user_id_str else None
        email: str = payload.get("email")
        exp: Optional[int] = payload.get("exp")

        if user_id is None or email is None:
            raise credentials_exception

        # Check if token has expired (use UTC consistently)
        if exp is not None:
            exp_datetime = datetime.utcfromtimestamp(exp)
            if exp_datetime < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    except JWTError:
        raise credentials_exception

    # Retrieve user from database
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.

    Args:
        current_user: Authenticated user

    Returns:
        User: Active user
    """
    return current_user


def verify_user_id_match(
    url_user_id: int,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Verify that URL user_id matches JWT user_id.

    Args:
        url_user_id: User ID from URL path
        current_user: Authenticated user from JWT

    Returns:
        User: Authenticated user

    Raises:
        HTTPException: If user IDs don't match
    """
    if url_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user ID mismatch"
        )
    return current_user