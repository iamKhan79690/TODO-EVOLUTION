"""Authentication schemas for request and response models."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from sqlmodel import SQLModel


# Base schemas
class UserBase(SQLModel):
    """Base user schema."""
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=255, description="User display name")


class UserRead(UserBase):
    """User response schema."""
    id: int
    created_at: datetime
    updated_at: datetime


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=1, max_length=128, description="User password")


class UserUpdate(BaseModel):
    """User update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None


# Authentication schemas
class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """JWT token data schema."""
    user_id: Optional[int] = None
    email: Optional[str] = None


class SignUpRequest(UserCreate):
    """Sign up request schema."""
    confirm_password: Optional[str] = None

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that passwords match if confirm_password is provided."""
        if v is not None and 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class SignInRequest(BaseModel):
    """Sign in request schema."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class SignOutRequest(BaseModel):
    """Sign out request schema."""
    refresh_token: str = Field(..., description="Refresh token to revoke")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str = Field(..., description="Refresh token")


class AuthResponse(BaseModel):
    """Authentication response schema."""
    user: UserRead
    token: Token
    message: str = "Authentication successful"


class AuthError(BaseModel):
    """Authentication error response schema."""
    error: str
    message: str
    details: Optional[dict] = None


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    email: EmailStr = Field(..., description="User email address")


class PasswordReset(BaseModel):
    """Password reset schema."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that passwords match."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class PasswordChange(BaseModel):
    """Password change schema."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that passwords match."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# Session management schemas
class SessionInfo(BaseModel):
    """Session information schema."""
    session_id: str
    created_at: datetime
    last_accessed: datetime
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True


class UserSessions(BaseModel):
    """User sessions response schema."""
    user: UserRead
    sessions: list[SessionInfo]


# Email verification schemas
class EmailVerificationRequest(BaseModel):
    """Email verification request schema."""
    email: EmailStr = Field(..., description="User email address")


class EmailVerification(BaseModel):
    """Email verification schema."""
    token: str = Field(..., description="Email verification token")


class VerifyEmailResponse(BaseModel):
    """Email verification response schema."""
    success: bool
    message: str
    user: Optional[UserRead] = None