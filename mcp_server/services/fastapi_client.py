"""
FastAPI HTTP Client for MCP Server Integration.

Provides HTTP client functionality for the MCP server to communicate
with the FastAPI backend for task operations and user data.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from uuid import UUID

import httpx
import structlog
from httpx import AsyncClient, Response
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class FastAPIClient:
    """
    HTTP client for communicating with the FastAPI backend.

    Handles authentication, retries, and error handling for all MCP-to-backend
    communication including task operations, user data, and conversation management.
    """

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0):
        """
        Initialize the FastAPI client.

        Args:
            base_url: Base URL of the FastAPI backend
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client: Optional[AsyncClient] = None

        # Common headers that will be used for all requests
        self.default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "MCP-Server/1.0"
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Initialize the HTTP client."""
        if self.client is None:
            self.client = AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self.default_headers
            )
            logger.info("FastAPI HTTP client started", base_url=self.base_url)

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("FastAPI HTTP client closed")

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        user_id: int,
        jwt_token: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated HTTP request to the FastAPI backend.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            user_id: User ID for the request
            jwt_token: JWT authentication token
            data: Request body data
            params: Query parameters

        Returns:
            Response data as dictionary

        Raises:
            APIError: If the request fails
        """
        if not self.client:
            await self.start()

        url = f"{self.base_url}{endpoint}"
        headers = {
            **self.default_headers,
            "Authorization": f"Bearer {jwt_token}"
        }

        try:
            logger.debug("Making HTTP request",
                        method=method,
                        url=url,
                        user_id=user_id,
                        endpoint=endpoint)

            response = await self.client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers
            )

            # Log response details
            logger.debug("HTTP response received",
                        status_code=response.status_code,
                        user_id=user_id,
                        endpoint=endpoint)

            # Handle different response codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 201:
                return response.json()
            elif response.status_code == 404:
                raise APIError(f"Resource not found: {endpoint}", response.status_code)
            elif response.status_code == 401:
                raise APIError("Authentication failed", response.status_code)
            elif response.status_code == 403:
                raise APIError("Access forbidden", response.status_code)
            elif response.status_code >= 400:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    error_data = {"detail": response.text}
                raise APIError(
                    f"API request failed: {response.status_code}",
                    response.status_code,
                    error_data
                )
            else:
                return response.json() if response.content else {}

        except httpx.TimeoutException:
            raise APIError(f"Request timeout: {endpoint}")
        except httpx.ConnectError:
            raise APIError(f"Connection error: {endpoint}")
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error: {str(e)}")
        except json.JSONDecodeError:
            raise APIError(f"Invalid JSON response from: {endpoint}")

    # Task Operations
    async def create_task(
        self,
        user_id: int,
        jwt_token: str,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new task for a user.

        Args:
            user_id: User ID
            jwt_token: Authentication token
            title: Task title
            description: Task description
            priority: Task priority (low, medium, high, urgent)
            due_date: Optional due date (ISO string)

        Returns:
            Created task data
        """
        data = {
            "title": title,
            "priority": priority
        }
        if description:
            data["description"] = description
        if due_date:
            data["due_date"] = due_date

        return await self._make_request(
            method="POST",
            endpoint=f"/api/{user_id}/tasks",
            user_id=user_id,
            jwt_token=jwt_token,
            data=data
        )

    async def get_user_tasks(
        self,
        user_id: int,
        jwt_token: str,
        limit: int = 50,
        offset: int = 0,
        completed: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Get tasks for a user.

        Args:
            user_id: User ID
            jwt_token: Authentication token
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip
            completed: Filter by completion status

        Returns:
            List of tasks
        """
        params = {"limit": limit, "offset": offset}
        if completed is not None:
            params["completed"] = completed

        return await self._make_request(
            method="GET",
            endpoint=f"/api/{user_id}/tasks",
            user_id=user_id,
            jwt_token=jwt_token,
            params=params
        )

    async def update_task(
        self,
        user_id: int,
        jwt_token: str,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        is_completed: Optional[bool] = None,
        due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing task.

        Args:
            user_id: User ID
            jwt_token: Authentication token
            task_id: Task ID
            title: New task title
            description: New task description
            priority: New task priority
            is_completed: New completion status
            due_date: New due date

        Returns:
            Updated task data
        """
        data = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if priority is not None:
            data["priority"] = priority
        if is_completed is not None:
            data["is_completed"] = is_completed
        if due_date is not None:
            data["due_date"] = due_date

        return await self._make_request(
            method="PUT",
            endpoint=f"/api/{user_id}/tasks/{task_id}",
            user_id=user_id,
            jwt_token=jwt_token,
            data=data
        )

    async def complete_task(
        self,
        user_id: int,
        jwt_token: str,
        task_id: int
    ) -> Dict[str, Any]:
        """
        Mark a task as completed.

        Args:
            user_id: User ID
            jwt_token: Authentication token
            task_id: Task ID

        Returns:
            Updated task data
        """
        return await self.update_task(
            user_id=user_id,
            jwt_token=jwt_token,
            task_id=task_id,
            is_completed=True
        )

    async def delete_task(
        self,
        user_id: int,
        jwt_token: str,
        task_id: int
    ) -> Dict[str, Any]:
        """
        Delete a task.

        Args:
            user_id: User ID
            jwt_token: Authentication token
            task_id: Task ID

        Returns:
            Deletion confirmation
        """
        return await self._make_request(
            method="DELETE",
            endpoint=f"/api/{user_id}/tasks/{task_id}",
            user_id=user_id,
            jwt_token=jwt_token
        )

    # User Operations
    async def get_user_info(
        self,
        user_id: int,
        jwt_token: str
    ) -> Dict[str, Any]:
        """
        Get user information.

        Args:
            user_id: User ID
            jwt_token: Authentication token

        Returns:
            User data
        """
        return await self._make_request(
            method="GET",
            endpoint=f"/api/{user_id}/profile",
            user_id=user_id,
            jwt_token=jwt_token
        )

    # Chat/Conversation Operations
    async def create_conversation(
        self,
        user_id: int,
        jwt_token: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation.

        Args:
            user_id: User ID
            jwt_token: Authentication token
            title: Optional conversation title

        Returns:
            Created conversation data
        """
        data = {}
        if title:
            data["title"] = title

        return await self._make_request(
            method="POST",
            endpoint=f"/api/chat/conversations",
            user_id=user_id,
            jwt_token=jwt_token,
            data=data
        )

    async def get_user_conversations(
        self,
        user_id: int,
        jwt_token: str,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get user's conversations.

        Args:
            user_id: User ID
            jwt_token: Authentication token
            limit: Maximum number of conversations
            offset: Number of conversations to skip

        Returns:
            List of conversations
        """
        params = {"limit": limit, "offset": offset}

        return await self._make_request(
            method="GET",
            endpoint=f"/api/chat/conversations",
            user_id=user_id,
            jwt_token=jwt_token,
            params=params
        )

    async def create_message(
        self,
        user_id: int,
        jwt_token: str,
        conversation_id: UUID,
        content: str,
        role: str = "user",
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Create a new message in a conversation.

        Args:
            user_id: User ID
            jwt_token: Authentication token
            conversation_id: Conversation ID
            content: Message content
            role: Message role (user, assistant, system)
            message_type: Type of message (text, image, file, operation_result)

        Returns:
            Created message data
        """
        data = {
            "conversation_id": str(conversation_id),
            "content": content,
            "role": role,
            "message_type": message_type
        }

        return await self._make_request(
            method="POST",
            endpoint=f"/api/chat/messages",
            user_id=user_id,
            jwt_token=jwt_token,
            data=data
        )

    async def get_conversation_messages(
        self,
        user_id: int,
        jwt_token: str,
        conversation_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get messages in a conversation.

        Args:
            user_id: User ID
            jwt_token: Authentication token
            conversation_id: Conversation ID
            limit: Maximum number of messages
            offset: Number of messages to skip

        Returns:
            List of messages
        """
        params = {
            "conversation_id": str(conversation_id),
            "limit": limit,
            "offset": offset
        }

        return await self._make_request(
            method="GET",
            endpoint=f"/api/chat/messages",
            user_id=user_id,
            jwt_token=jwt_token,
            params=params
        )

    # Health Check
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the FastAPI backend.

        Returns:
            Health status information
        """
        try:
            return await self._make_request(
                method="GET",
                endpoint="/api/health",
                user_id=0,  # Health check doesn't require user_id
                jwt_token="health-check-token"
            )
        except APIError as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "status_code": e.status_code
            }

    # Utility Methods
    async def validate_token(self, jwt_token: str) -> bool:
        """
        Validate a JWT token with the backend.

        Args:
            jwt_token: JWT token to validate

        Returns:
            True if token is valid, False otherwise
        """
        try:
            response = await self._make_request(
                method="GET",
                endpoint="/api/auth/validate",
                user_id=0,
                jwt_token=jwt_token
            )
            return response.get("valid", False)
        except APIError:
            return False

    async def get_task_statistics(
        self,
        user_id: int,
        jwt_token: str
    ) -> Dict[str, Any]:
        """
        Get task statistics for a user.

        Args:
            user_id: User ID
            jwt_token: Authentication token

        Returns:
            Task statistics
        """
        return await self._make_request(
            method="GET",
            endpoint=f"/api/{user_id}/tasks/stats",
            user_id=user_id,
            jwt_token=jwt_token
        )


# Global client instance
fastapi_client = FastAPIClient()


# Context manager for easy usage
async def with_fastapi_client(base_url: str = None, timeout: float = None):
    """
    Context manager for using FastAPI client.

    Args:
        base_url: Optional base URL override
        timeout: Optional timeout override

    Yields:
        FastAPIClient instance
    """
    client = FastAPIClient(
        base_url=base_url or "http://localhost:8000",
        timeout=timeout or 30.0
    )

    async with client:
        yield client