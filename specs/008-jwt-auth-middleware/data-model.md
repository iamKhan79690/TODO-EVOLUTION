# Data Model: JWT Authentication Middleware

**Date**: 2025-01-13
**Feature**: JWT Authentication Middleware
**Status**: Complete

## Overview

The JWT authentication middleware is a stateless component that processes authentication without persisting data. However, it defines structured interfaces for user information and authentication events that flow through the system.

## Key Data Structures

### User Claims Model

The JWT claims structure that the middleware expects and processes:

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserClaims(BaseModel):
    """JWT token claims structure expected by the middleware"""
    user_id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    exp: datetime = Field(..., description="Token expiration timestamp")
    iat: Optional[datetime] = Field(None, description="Token issued timestamp")
    iss: Optional[str] = Field(None, description="Token issuer")
    aud: Optional[str] = Field(None, description="Token audience")

    class Config:
        json_encoders = {
            datetime: lambda v: v.timestamp()
        }
```

### Request State Model

The user information attached to FastAPI request state:

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuthenticatedUser(BaseModel):
    """User information attached to request.state after successful authentication"""
    user_id: str = Field(..., description="Authenticated user ID")
    email: str = Field(..., description="User email address")
    exp: datetime = Field(..., description="Token expiration time")
    token_issued_at: Optional[datetime] = Field(None, description="When token was issued")

    @property
    def is_expired(self) -> bool:
        """Check if the authentication has expired"""
        return datetime.utcnow() > self.exp

class RequestState(BaseModel):
    """Extended request state with authentication information"""
    user: Optional[AuthenticatedUser] = Field(None, description="Authenticated user if present")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID for tracing")
    authentication_result: Optional[str] = Field(None, description="Authentication result: success/failed/invalid")
```

### Authentication Event Model

Structured data for audit logging and security monitoring:

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AuthenticationStatus(str, Enum):
    SUCCESS = "success"
    INVALID_TOKEN = "invalid_token"
    EXPIRED_TOKEN = "expired_token"
    MISSING_TOKEN = "missing_token"
    MALFORMED_TOKEN = "malformed_token"
    SIGNATURE_ERROR = "signature_error"

class AuthenticationEvent(BaseModel):
    """Audit event for authentication attempts"""
    timestamp: datetime = Field(..., description="Event timestamp")
    correlation_id: str = Field(..., description="Request correlation ID")
    status: AuthenticationStatus = Field(..., description="Authentication status")
    user_id: Optional[str] = Field(None, description="User ID if available")
    client_ip: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    endpoint: Optional[str] = Field(None, description="Requested endpoint")
    error_message: Optional[str] = Field(None, description="Error details for failed authentication")
    token_issued_at: Optional[datetime] = Field(None, description="When token was issued")
    token_expires_at: Optional[datetime] = Field(None, description="When token expires")

    class Config:
        json_encoders = {
            datetime: lambda v: v.timestamp()
        }

class SecurityAlert(BaseModel):
    """Security alert for suspicious authentication activity"""
    timestamp: datetime = Field(..., description="Alert timestamp")
    alert_type: str = Field(..., description="Type of security alert")
    correlation_id: str = Field(..., description="Request correlation ID")
    user_id: Optional[str] = Field(None, description="User ID if available")
    client_ip: str = Field(..., description="Client IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    threat_level: str = Field(..., description="Threat assessment level")
    details: Dict[str, Any] = Field(default_factory=dict, description="Alert details")
```

### Configuration Model

Middleware configuration with validation:

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class JWTMiddlewareConfig(BaseModel):
    """Configuration for JWT authentication middleware"""
    secret_key: str = Field(..., min_length=32, description="Secret key for JWT signing")
    algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    audience: Optional[str] = Field(None, description="Expected token audience")
    issuer: Optional[str] = Field(None, description="Expected token issuer")
    cookie_name: Optional[str] = Field(None, description="Cookie name for token (alternative to header)")
    header_name: str = Field(default="Authorization", description="Header name for token")
    header_scheme: str = Field(default="Bearer", description="Authorization header scheme")

    @validator('algorithm')
    def validate_algorithm(cls, v):
        allowed_algorithms = ['HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512']
        if v not in allowed_algorithms:
            raise ValueError(f"Algorithm must be one of {allowed_algorithms}")
        return v

    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v
```

## Data Flow

### Authentication Request Flow

```
HTTP Request
    ↓
Extract Token (Header or Cookie)
    ↓
Validate Token Format
    ↓
Verify Signature
    ↓
Decode Claims
    ↓
Validate Claims (user_id, email, exp)
    ↓
Check Expiration
    ↓
Attach User to request.state
    ↓
Proceed to Endpoint
```

### Error Handling Flow

```
HTTP Request
    ↓
Extract Token → Failed → Log Event → Return 401
Extract Token → Invalid Format → Log Event → Return 401
Verify Signature → Failed → Log Event → Return 401
Decode Claims → Failed → Log Event → Return 401
Validate Claims → Failed → Log Event → Return 401
Check Expiration → Expired → Log Event → Return 401
```

## Validation Rules

### Token Validation

1. **Format Validation**:
   - Token must have 3 parts (header.payload.signature)
   - Each part must be valid base64url encoding
   - Token length must be reasonable (<4096 characters)

2. **Signature Validation**:
   - Token signature must verify with secret key
   - Algorithm must match expected algorithm
   - Token must not be tampered with

3. **Claims Validation**:
   - user_id must be present and non-empty
   - email must be valid email format
   - exp must be present and in the future
   - iat must be before exp (if present)

4. **Security Validation**:
   - Token must not be blacklisted (if implemented)
   - User must exist in system (if user validation enabled)
   - Request must not exceed rate limits

### Security Monitoring Rules

1. **Failed Authentication Thresholds**:
   - >5 failed attempts per IP in 5 minutes
   - >10 failed attempts per user in 1 hour
   - >100 failed attempts system-wide in 1 minute

2. **Suspicious Pattern Detection**:
   - Sequential failed attempts with different tokens
   - Requests from known malicious IPs
   - Unusual user agent patterns
   - Token replay attempts

## Performance Considerations

### Memory Usage

- Middleware is stateless (no persistent storage)
- Token validation is O(1) cryptographic operations
- Audit logging uses memory-efficient structured logging
- No database connections or external dependencies

### CPU Usage

- JWT verification is optimized with efficient algorithms
- Asynchronous processing prevents blocking
- Lazy evaluation of expensive operations
- Minimal computational overhead per request

### Network Impact

- No external API calls during authentication
- All validation performed locally
- No additional network latency
- Compatible with existing request flow

## Integration Points

### FastAPI Integration

The middleware integrates with FastAPI through:

1. **ASGI Middleware Interface**:
   ```python
   app.add_middleware(JWTAuthMiddleware, secret_key=BETTER_AUTH_SECRET)
   ```

2. **Request State Access**:
   ```python
   @app.get("/protected")
   async def protected_endpoint(request: Request):
       user = getattr(request.state, 'user', None)
       if not user:
           raise HTTPException(status_code=401, detail="Unauthorized")
   ```

3. **Dependency Injection** (Alternative):
   ```python
   from fastapi import Depends

   def get_current_user(request: Request):
       return getattr(request.state, 'user', None)
   ```

### Logging Integration

The middleware integrates with existing logging through:

1. **Structured Logging**: JSON format for log aggregation
2. **Correlation IDs**: Request tracing across services
3. **Security Events**: Dedicated security alert channels
4. **Performance Metrics**: Authentication timing and success rates

## Security Properties

### Confidentiality

- User credentials never exposed in error messages
- Detailed security information only in internal logs
- Token validation prevents unauthorized access
- No sensitive data in audit logs (user IDs only)

### Integrity

- JWT signatures prevent token tampering
- Cryptographic verification ensures data integrity
- Request state protection through middleware chain
- Audit trail immutability through structured logging

### Availability

- Stateless middleware prevents single points of failure
- Fast authentication prevents performance degradation
- Graceful error handling maintains service availability
- Rate limiting prevents denial of service attacks

## Compliance Considerations

### Data Protection

- No PII exposure in client responses
- Audit trails for compliance reporting
- Token expiration ensures session management
- User access logging for accountability

### Security Standards

- Follows OWASP JWT best practices
- Implements proper error handling
- Provides comprehensive audit logging
- Supports security monitoring and alerting