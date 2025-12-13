"""Token blacklist store for JWT token management."""

import json
from typing import Optional, Set
from datetime import datetime, timedelta
from redis import asyncio as aioredis
from src.core.config import settings


class TokenBlacklist:
    """Redis-based token blacklist for JWT tokens."""

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self._connected = False
        # Always initialize in-memory fallback
        self._blacklisted_tokens: Set[str] = set()
        self._token_expiry: dict[str, datetime] = {}

    async def connect(self):
        """Connect to Redis if enabled."""
        if self._connected:
            return
            
        # Check if Redis is disabled in settings
        if not getattr(settings, 'REDIS_ENABLED', True):
            self._connected = False
            return
            
        try:
            # Try to connect to Redis
            self.redis = aioredis.from_url(
                getattr(settings, 'REDIS_URL', "redis://localhost:6379"),
                decode_responses=True,
                socket_timeout=5
            )
            # Test connection
            await self.redis.ping()
            self._connected = True
        except Exception:
            # Fallback to in-memory store if Redis is not available
            self._connected = False

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self._connected = False

    async def blacklist_token(self, token: str, expires_at: datetime):
        """Add token to blacklist."""
        await self.connect()

        if self.redis and self._connected:
            # Use Redis with TTL
            ttl = int((expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                await self.redis.setex(f"blacklist:{token}", ttl, "1")
        else:
            # Fallback to in-memory storage
            self._blacklisted_tokens.add(token)
            self._token_expiry[token] = expires_at

    async def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        await self.connect()

        if self.redis and self._connected:
            # Check Redis
            result = await self.redis.get(f"blacklist:{token}")
            return result is not None
        else:
            # Check in-memory storage and clean up expired tokens
            now = datetime.utcnow()
            expired_tokens = [
                token for token, expiry in self._token_expiry.items()
                if expiry <= now
            ]

            for token in expired_tokens:
                self._blacklisted_tokens.discard(token)
                del self._token_expiry[token]

            return token in self._blacklisted_tokens

    async def cleanup_expired_tokens(self):
        """Clean up expired tokens from in-memory storage."""
        if hasattr(self, '_blacklisted_tokens'):
            now = datetime.utcnow()
            expired_tokens = [
                token for token, expiry in self._token_expiry.items()
                if expiry <= now
            ]

            for token in expired_tokens:
                self._blacklisted_tokens.discard(token)
                del self._token_expiry[token]


# Global token blacklist instance
token_blacklist = TokenBlacklist()