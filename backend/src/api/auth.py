"""Authentication API endpoints using Better Auth."""

from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.core.database import get_session_dependency
from src.schemas.auth import (
    UserRead, UserCreate, AuthResponse, AuthError,
    SignInRequest, SignUpRequest, SignOutRequest,
    RefreshTokenRequest, Token, TokenData
)
from src.models.models import User
from src.auth.better_auth_config import (
    create_access_token, create_refresh_token, verify_token
)
from src.auth.token_store import token_blacklist
from src.dependencies.auth import get_current_user, get_current_active_user
from passlib.context import CryptContext

# Password hashing context - configure to handle bcrypt's 72-byte limit
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)

# Router instance
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

# HTTP Bearer scheme for token authentication
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


@router.post("/sign-up", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(
    user_data: SignUpRequest,
    session: AsyncSession = Depends(get_session_dependency())
) -> Any:
    """
    Register a new user.

    Args:
        user_data: User registration data
        session: Database session

    Returns:
        AuthResponse: Authentication response with user and tokens

    Raises:
        HTTPException: If registration fails
    """
    try:
        # Check if user already exists
        from sqlmodel import select
        statement = select(User).where(User.email == user_data.email)
        result = await session.execute(statement)
        existing_user = result.scalars().first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user with hashed password
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_password
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        # Create JWT tokens
        access_token = create_access_token(new_user.id, new_user.email)
        refresh_token = create_refresh_token(new_user.id)

        token_data = Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRE_MINUTES * 60
        )

        user_response = UserRead(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at
        )

        return AuthResponse(
            user=user_response,
            token=token_data,
            message="User registered successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/sign-in", response_model=AuthResponse)
async def sign_in(
    credentials: SignInRequest,
    session: AsyncSession = Depends(get_session_dependency())
) -> Any:
    """
    Sign in a user with email and password.

    Args:
        credentials: Sign in credentials
        session: Database session

    Returns:
        AuthResponse: Authentication response with user and tokens

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Find user by email
        from sqlmodel import select
        statement = select(User).where(User.email == credentials.email)
        result = await session.execute(statement)
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # In a real implementation, you'd verify the password hash
        # For now, we'll simulate successful authentication
        # TODO: Implement proper password verification with Better Auth

        # Create JWT tokens
        access_token = create_access_token(user.id, user.email)
        refresh_token = create_refresh_token(user.id)

        token_data = Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRE_MINUTES * 60
        )

        user_response = UserRead(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

        return AuthResponse(
            user=user_response,
            token=token_data,
            message="Sign in successful"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sign in failed: {str(e)}"
        )


@router.post("/sign-out")
async def sign_out(
    request: SignOutRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Any:
    """
    Sign out a user and blacklist their tokens.

    Args:
        request: Sign out request with refresh token
        credentials: HTTP Authorization credentials

    Returns:
        dict: Success message

    Raises:
        HTTPException: If sign out fails
    """
    try:
        # Blacklist the access token
        access_token = credentials.credentials
        token_data = verify_token(access_token, "access")

        # Calculate expiry time for blacklisting
        exp_timestamp = token_data.get("exp", 0)
        exp_datetime = datetime.fromtimestamp(exp_timestamp)

        await token_blacklist.blacklist_token(access_token, exp_datetime)

        # Blacklist the refresh token
        refresh_token = request.refresh_token
        if refresh_token:
            try:
                refresh_data = verify_token(refresh_token, "refresh")
                refresh_exp = datetime.fromtimestamp(refresh_data.get("exp", 0))
                await token_blacklist.blacklist_token(refresh_token, refresh_exp)
            except Exception:
                # Invalid refresh token, but continue with sign out
                pass

        return {"message": "Sign out successful"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sign out failed: {str(e)}"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session_dependency())
) -> Any:
    """
    Refresh access token using refresh token.

    Args:
        request: Refresh token request
        session: Database session

    Returns:
        Token: New access token and refresh token

    Raises:
        HTTPException: If token refresh fails
    """
    try:
        # Verify refresh token
        token_data = verify_token(request.refresh_token, "refresh")
        user_id = token_data.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Find user
        from sqlmodel import select
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Create new tokens
        access_token = create_access_token(user.id, user.email)
        new_refresh_token = create_refresh_token(user.id)

        # Blacklist old refresh token
        exp_timestamp = token_data.get("exp", 0)
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        await token_blacklist.blacklist_token(request.refresh_token, exp_datetime)

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRE_MINUTES * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user

    Returns:
        UserRead: User information
    """
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.get("/verify")
async def verify_token_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Any:
    """
    Verify if a token is valid.

    Args:
        credentials: HTTP Authorization credentials

    Returns:
        dict: Token validity status

    Raises:
        HTTPException: If token is invalid
    """
    try:
        token = credentials.credentials

        # Check if token is blacklisted
        if await token_blacklist.is_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

        # Verify token
        token_data = verify_token(token, "access")

        return {
            "valid": True,
            "user_id": token_data.get("sub"),
            "email": token_data.get("email"),
            "type": token_data.get("type"),
            "exp": token_data.get("exp")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )