"""
JWT Authentication Configuration for MCP Server

Handles JWT token validation and user context extraction for Phase III AI Chatbot integration.
"""

import os
from pathlib import Path

# Load .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

import jwt
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException


class JWTConfig:
    """JWT configuration and validation class."""

    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")  # Must match backend

        if not self.secret_key:
            raise ValueError("JWT_SECRET environment variable is required")

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token and extract user context.

        Args:
            token: JWT token string

        Returns:
            Dictionary containing user context (user_id, email, name)

        Raises:
            ValueError: If token is invalid, expired, or malformed
        """
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # Extract required user context
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("JWT token missing user ID (sub claim)")

            email = payload.get("email", "")
            name = payload.get("name", "")

            # Return user context
            return {
                "user_id": int(user_id) if user_id.isdigit() else user_id,
                "email": email,
                "name": name,
                "exp": payload.get("exp"),
                "iat": payload.get("iat")
            }

        except jwt.ExpiredSignatureError:
            raise ValueError("JWT token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid JWT token: {str(e)}")
        except Exception as e:
            raise ValueError(f"JWT validation error: {str(e)}")

    def is_token_expired(self, token: str) -> bool:
        """
        Check if JWT token is expired without raising exception.

        Args:
            token: JWT token string

        Returns:
            True if token is expired, False otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )

            exp = payload.get("exp")
            if exp:
                return datetime.fromtimestamp(exp) < datetime.utcnow()

            return False

        except jwt.InvalidTokenError:
            return True
        except Exception:
            return True

    def get_token_remaining_time(self, token: str) -> Optional[timedelta]:
        """
        Get remaining time until token expires.

        Args:
            token: JWT token string

        Returns:
            Timedelta until expiration, or None if cannot determine
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )

            exp = payload.get("exp")
            if exp:
                exp_datetime = datetime.fromtimestamp(exp)
                remaining = exp_datetime - datetime.utcnow()
                return remaining if remaining.total_seconds() > 0 else timedelta(0)

            return None

        except Exception:
            return None


# Global JWT configuration instance
jwt_config = JWTConfig()


def validate_jwt_token(token: str) -> Dict[str, Any]:
    """
    Convenience function to validate JWT token.

    Args:
        token: JWT token string

    Returns:
        User context dictionary

    Raises:
        ValueError: If token is invalid
    """
    return jwt_config.validate_token(token)


def create_http_exception_from_jwt_error(error: Exception) -> HTTPException:
    """
    Convert JWT validation error to HTTPException.

    Args:
        error: JWT validation exception

    Returns:
        HTTPException with appropriate status code and message
    """
    error_message = str(error)

    if "expired" in error_message.lower():
        return HTTPException(
            status_code=401,
            detail="JWT token has expired"
        )
    elif "invalid" in error_message.lower():
        return HTTPException(
            status_code=401,
            detail="Invalid JWT token"
        )
    else:
        return HTTPException(
            status_code=401,
            detail="Authentication failed"
        )