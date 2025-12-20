# JWT Authentication Middleware Quickstart Guide

**Version**: 1.0.0
**Date**: 2025-01-13
**Feature**: JWT Authentication Middleware

## Overview

This guide shows how to quickly integrate the JWT authentication middleware into your FastAPI application. The middleware provides secure token-based authentication with comprehensive audit logging.

## Prerequisites

- Python 3.13+
- FastAPI application
- JWT tokens issued by your authentication system
- Environment variable `BETTER_AUTH_SECRET` configured

## Quick Start

### 1. Install Dependencies

```bash
pip install fastapi "python-jose[cryptography]" structlog python-multipart uvicorn
```

### 2. Basic Middleware Setup

Create the JWT authentication middleware file:

```python
# src/middleware/auth.py
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import structlog

logger = structlog.get_logger(__name__)

class JWTAuthMiddleware:
    """JWT Authentication Middleware for FastAPI"""

    def __init__(
        self,
        app,
        secret_key: str,
        algorithm: str = "HS256",
        audience: Optional[str] = None,
        issuer: Optional[str] = None,
        header_name: str = "Authorization",
        header_scheme: str = "Bearer"
    ):
        self.app = app
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.audience = audience
        self.issuer = issuer
        self.header_name = header_name
        self.header_scheme = header_scheme

        # HTTP Bearer scheme for error responses
        self.security = HTTPBearer(
            scheme_name=self.header_scheme,
            auto_error=False
        )

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable) -> Response:
        """ASGI middleware entry point"""

        # Create Request object from scope
        request = Request(scope, receive)

        # Add correlation ID to request state
        request.state.correlation_id = self._get_correlation_id(request)

        # Skip authentication for certain paths
        if self._should_skip_auth(request.url.path):
            return await self.app(scope, receive, send)

        try:
            # Extract and validate token
            token = self._extract_token(request)
            if not token:
                return await self._handle_auth_error(
                    request, "Authentication required", "AUTHENTICATION_REQUIRED"
                )

            # Validate token and extract claims
            claims = await self._validate_token(token)

            # Attach user context to request state
            request.state.user = {
                "user_id": claims["sub"],
                "email": claims["email"],
                "expires_at": datetime.fromtimestamp(claims["exp"], tz=timezone.utc),
                "token_issued_at": datetime.fromtimestamp(claims.get("iat", 0), tz=timezone.utc)
            }

            # Log successful authentication
            await self._log_authentication_event("success", request, claims)

            # Continue with request processing
            return await self.app(scope, receive, send)

        except Exception as e:
            # Handle authentication errors
            return await self._handle_authentication_exception(request, e)

    def _get_correlation_id(self, request: Request) -> str:
        """Generate or extract correlation ID from request"""
        # Try to get from header first
        correlation_id = request.headers.get("X-Correlation-ID") or request.headers.get("x-correlation-id")

        if not correlation_id:
            # Generate new correlation ID
            import uuid
            correlation_id = str(uuid.uuid4())

        return correlation_id

    def _should_skip_auth(self, path: str) -> bool:
        """Check if authentication should be skipped for this path"""
        # Skip authentication for health checks and documentation
        skip_paths = [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico",
            "/static"
        ]

        return any(path.startswith(skip_path) for skip_path in skip_paths)

    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request"""
        # Try to get from Authorization header
        authorization = request.headers.get(self.header_name)
        if authorization:
            # Extract token from "Bearer <token>" format
            parts = authorization.split()
            if len(parts) == 2 and parts[0].lower() == self.header_scheme.lower():
                return parts[1]

        return None

    async def _validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return claims"""
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer
            )

            # Validate required claims
            if "sub" not in payload:
                raise ValueError("Token missing required 'sub' claim")

            if "email" not in payload:
                raise ValueError("Token missing required 'email' claim")

            if "exp" not in payload:
                raise ValueError("Token missing required 'exp' claim")

            # Check expiration
            if datetime.fromtimestamp(payload["exp"], tz=timezone.utc) < datetime.now(timezone.utc):
                raise ValueError("Token has expired")

            return payload

        except jwt.ExpiredSignatureError as e:
            raise ValueError(f"Token has expired: {str(e)}")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")
        except Exception as e:
            raise ValueError(f"Token validation failed: {str(e)}")

    async def _handle_auth_error(
        self,
        request: Request,
        message: str,
        error_code: str
    ) -> Response:
        """Handle authentication error and return appropriate response"""

        # Log authentication failure
        await self._log_authentication_event("failed", request, {"error": error_code})

        # Create error response
        error_response = {
            "detail": message,
            "error_code": error_code,
            "correlation_id": request.state.correlation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "method": request.method
        }

        return Response(
            content=str(error_response).encode(),
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={
                "Content-Type": "application/json",
                "WWW-Authenticate": f'{self.header_scheme} realm="Todo Evolution API"',
                "X-Correlation-ID": request.state.correlation_id
            }
        )

    async def _handle_authentication_exception(
        self,
        request: Request,
        exception: Exception
    ) -> Response:
        """Handle authentication exception and return appropriate response"""

        # Determine error type from exception
        error_code = "AUTHENTICATION_ERROR"
        message = "Authentication failed"

        if "expired" in str(exception).lower():
            error_code = "EXPIRED_TOKEN"
            message = "Authentication token has expired"
        elif "invalid" in str(exception).lower() or "malformed" in str(exception).lower():
            error_code = "INVALID_TOKEN"
            message = "Invalid authentication token"
        elif "signature" in str(exception).lower():
            error_code = "SIGNATURE_ERROR"
            message = "Invalid token signature"

        return await self._handle_auth_error(request, message, error_code)

    async def _log_authentication_event(
        self,
        status: str,
        request: Request,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log authentication event"""

        event_data = {
            "event_type": "authentication",
            "status": status,
            "correlation_id": request.state.correlation_id,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "endpoint": str(request.url.path),
            "method": request.method,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Add user data if available
        if hasattr(request.state, 'user') and request.state.user:
            event_data["user_id"] = request.state.user["user_id"]

        # Add additional data
        if additional_data:
            event_data.update(additional_data)

        # Log the event
        logger.info("Authentication event", **event_data)
```

### 3. Add Middleware to FastAPI App

```python
# main.py
from fastapi import FastAPI
from src.middleware.auth import JWTAuthMiddleware
import os

app = FastAPI(title="Todo Evolution API")

# Add JWT authentication middleware
app.add_middleware(
    JWTAuthMiddleware,
    secret_key=os.getenv("BETTER_AUTH_SECRET", "your-secret-key-32-chars"),
    algorithm="HS256",
    audience="todo-evolution-api",
    issuer="todo-evolution-auth"
)

# Your existing routes...
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/protected")
async def protected_route(request: Request):
    user = getattr(request.state, "user", None)
    return {"message": f"Hello {user['email'] if user else 'Anonymous'}!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4. Protect Endpoints

```python
from fastapi import Depends, HTTPException, status
from fastapi import Request

def get_current_user(request: Request):
    """Dependency to get current authenticated user"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user

@app.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Protected endpoint requiring authentication"""
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "expires_at": current_user["expires_at"]
    }

@app.get("/tasks")
async def get_tasks(current_user: dict = Depends(get_current_user)):
    """Protected endpoint for user tasks"""
    # User is authenticated, return their tasks
    return {"message": f"Tasks for user {current_user['email']}"}
```

### 5. Test the Implementation

Start your FastAPI application:

```bash
uvicorn main:app --reload
```

#### Test with Valid Token

```bash
# Test with a valid JWT token
curl -X GET "http://localhost:8000/protected" \
  -H "Authorization: Bearer YOUR_VALID_JWT_TOKEN"
```

Expected Response:
```json
{
  "message": "Hello user@example.com!"
}
```

#### Test with No Token

```bash
# Test without token
curl -X GET "http://localhost:8000/protected"
```

Expected Response:
```json
{
  "detail": "Authentication required",
  "error_code": "AUTHENTICATION_REQUIRED",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Test with Invalid Token

```bash
# Test with invalid token
curl -X GET "http://localhost:8000/protected" \
  -H "Authorization: Bearer invalid-token"
```

Expected Response:
```json
{
  "detail": "Invalid authentication token",
  "error_code": "INVALID_TOKEN",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Configuration

### Environment Variables

Create a `.env` file with your configuration:

```bash
# .env
BETTER_AUTH_SECRET=your-super-secret-jwt-key-32-chacters-long
JWT_ALGORITHM=HS256
JWT_AUDIENCE=todo-evolution-api
JWT_ISSUER=todo-evolution-auth
```

### Configuration Options

```python
# Advanced configuration
app.add_middleware(
    JWTAuthMiddleware,
    secret_key=os.getenv("BETTER_AUTH_SECRET"),
    algorithm="HS256",
    audience=os.getenv("JWT_AUDIENCE", "todo-evolution-api"),
    issuer=os.getenv("JWT_ISSUER", "todo-evolution-auth"),
    header_name="Authorization",
    header_scheme="Bearer"
)
```

## Testing

### Unit Tests

```python
# tests/test_middleware.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from src.middleware.auth import JWTAuthMiddleware
from jose import jwt
import os
from datetime import datetime, timezone, timedelta

def create_test_app():
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse

    app = FastAPI()

    # Add middleware
    app.add_middleware(
        JWTAuthMiddleware,
        secret_key="test-secret-key-32-characters",
        algorithm="HS256"
    )

    @app.get("/test")
    async def test_endpoint(request: Request):
        user = getattr(request.state, "user", None)
        return JSONResponse({"authenticated": user is not None})

    return app

def test_valid_token():
    app = create_test_app()
    client = TestClient(app)

    # Create valid token
    payload = {
        "sub": "test_user_123",
        "email": "test@example.com",
        "exp": (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp(),
        "iat": datetime.now(timezone.utc).timestamp()
    }
    token = jwt.encode(payload, "test-secret-key-32-characters", algorithm="HS256")

    response = client.get("/test", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["authenticated"] is True

def test_invalid_token():
    app = create_test_app()
    client = TestClient(app)

    response = client.get("/test", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401
    assert response.json()["error_code"] == "INVALID_TOKEN"

def test_missing_token():
    app = create_test_app()
    client = TestClient(app)

    response = client.get("/test")
    assert response.status_code == 401
    assert response.json()["error_code"] == "AUTHENTICATION_REQUIRED"

if __name__ == "__main__":
    test_valid_token()
    test_invalid_token()
    test_missing_token()
    print("All tests passed!")
```

## Security Features

### Audit Logging

The middleware automatically logs all authentication events with:

- ✅ **Correlation IDs**: Request tracing across services
- ✅ **Timestamps**: Precise event timing
- ✅ **Client Information**: IP addresses and user agents
- ✅ **User Details**: User IDs and outcomes
- ✅ **Security Events**: Failed authentication attempts

### Security Headers

The middleware adds security headers to responses:

- ✅ **WWW-Authenticate**: For 401 responses
- ✅ **X-Correlation-ID**: For request tracing
- ✅ **Content-Type**: JSON response formatting

### Token Validation

Comprehensive token validation includes:

- ✅ **Signature Verification**: Cryptographic signature validation
- ✅ **Expiration Check**: Token expiry validation
- ✅ **Claims Validation**: Required claims validation
- ✅ **Format Validation**: Token structure validation

## Troubleshooting

### Common Issues

#### "Secret key must be at least 32 characters"
```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### "Invalid token signature"
- Ensure `BETTER_AUTH_SECRET` matches between services
- Check that token was created with correct algorithm
- Verify token hasn't been modified

#### "Token has expired"
- Check system time synchronization
- Verify token expiration time
- Consider implementing token refresh

### Debug Logging

Enable debug logging to troubleshoot authentication issues:

```python
import structlog
import logging

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG)
structlog.configure(processors=[structlog.processors.JSONRenderer()])
```

### Monitoring

Monitor authentication metrics:

```python
# Add to your monitoring system
- Authentication success rate
- Authentication failure reasons
- Response time metrics
- Error rate alerts
- Security event monitoring
```

## Integration Examples

### With Better Auth

If you're using Better Auth for frontend authentication:

```python
# Frontend (Next.js)
const token = await signIn()  // Better Auth returns JWT
localStorage.setItem('auth_token', token)

# Backend (FastAPI)
# Middleware automatically validates Better Auth JWTs
# Ensure BETTER_AUTH_SECRET matches between services
```

### With Custom Auth

If you have a custom authentication system:

```python
# Your auth service
def create_jwt_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": (datetime.now() + timedelta(hours=1)).timestamp(),
        "iat": datetime.now().timestamp()
    }
    return jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")
```

## Production Considerations

### Performance Optimization

- Use efficient JWT algorithms (HS256 recommended)
- Implement connection pooling for high-volume requests
- Monitor memory usage in high-traffic scenarios
- Consider token caching if you have specific performance requirements

### Security Hardening

- Rotate secret keys regularly
- Implement token blacklisting if needed
- Add rate limiting for authentication endpoints
- Monitor for suspicious authentication patterns
- Implement token refresh mechanisms for better UX

### Monitoring and Alerting

- Set up alerts for high authentication failure rates
- Monitor response time performance
- Track security events and patterns
- Implement log aggregation and analysis
- Set up health checks for middleware functionality

## Support

For issues or questions:

1. Check the documentation: `docs/`
2. Review error messages and correlation IDs
3. Enable debug logging for troubleshooting
4. Check environment variable configuration
5. Verify token generation and validation consistency

This JWT authentication middleware provides secure, performant authentication with comprehensive audit logging for production applications.