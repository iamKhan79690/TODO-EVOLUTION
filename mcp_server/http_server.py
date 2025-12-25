"""
HTTP-based MCP Server for AI Agent Integration.

FastAPI wrapper that exposes MCP tools via HTTP endpoints.
Runs on port 8001 and provides endpoints for:
- /tools/add_task
- /tools/list_tasks
- /tools/complete_task
- /tools/delete_task
- /tools/update_task
"""

import os
import sys
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import structlog

# Configure logging
logger = structlog.get_logger(__name__)

# Backend API URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Create FastAPI app
app = FastAPI(
    title="MCP HTTP Server",
    description="HTTP wrapper for MCP tools",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ToolRequest(BaseModel):
    """Base request model for tool calls."""
    user_id: int
    jwt_token: str


class AddTaskRequest(ToolRequest):
    """Request model for add_task tool."""
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    due_date: Optional[str] = None


class ListTasksRequest(ToolRequest):
    """Request model for list_tasks tool."""
    status: Optional[str] = "all"
    limit: int = 20
    offset: int = 0


class CompleteTaskRequest(ToolRequest):
    """Request model for complete_task tool."""
    task_id: int


class DeleteTaskRequest(ToolRequest):
    """Request model for delete_task tool."""
    task_id: int


class UpdateTaskRequest(ToolRequest):
    """Request model for update_task tool."""
    task_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    tags: Optional[List[str]] = None


class ToolResponse(BaseModel):
    """Standard response model for tool calls."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


# Helper function to call backend API
async def call_backend_api(
    endpoint: str,
    method: str,
    jwt_token: str,
    data: Optional[Dict] = None
) -> Dict[str, Any]:
    """Call the backend FastAPI server."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{BACKEND_URL}{endpoint}"
            
            if method == "GET":
                response = await client.get(url, headers=headers, params=data)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=data)
            elif method == "PATCH":
                response = await client.patch(url, headers=headers, json=data)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            else:
                return {
                    "success": False,
                    "error": {
                        "code": f"HTTP_{response.status_code}",
                        "message": response.text[:500]
                    }
                }
                
    except httpx.ConnectError:
        return {
            "success": False,
            "error": {"code": "CONNECTION_ERROR", "message": "Backend server unavailable"}
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)}
        }


# Tool Endpoints

@app.post("/tools/add_task", response_model=ToolResponse)
async def add_task(request: AddTaskRequest):
    """
    Add a new task for the user.
    
    Calls the backend /api/tasks endpoint to create a task.
    """
    logger.info("add_task called", user_id=request.user_id, title=request.title)
    
    task_data = {
        "title": request.title,
        "description": request.description,
        "priority": request.priority or "medium",
    }
    
    if request.due_date:
        task_data["due_date"] = request.due_date
    
    result = await call_backend_api(
        endpoint="/api/tasks",
        method="POST",
        jwt_token=request.jwt_token,
        data=task_data
    )
    
    if result["success"]:
        return ToolResponse(
            success=True,
            data=result["data"],
            message=f"Task '{request.title}' created successfully!"
        )
    else:
        return ToolResponse(
            success=False,
            error=result.get("error"),
            message="Failed to create task"
        )


@app.post("/tools/list_tasks", response_model=ToolResponse)
async def list_tasks(request: ListTasksRequest):
    """
    List tasks for the user.
    
    Calls the backend /api/tasks endpoint with optional filters.
    """
    logger.info("list_tasks called", user_id=request.user_id, status=request.status)
    
    params = {
        "skip": request.offset,
        "limit": request.limit
    }
    
    # Add status filter if not "all"
    if request.status and request.status != "all":
        params["completed"] = request.status == "completed"
    
    result = await call_backend_api(
        endpoint="/api/tasks",
        method="GET",
        jwt_token=request.jwt_token,
        data=params
    )
    
    if result["success"]:
        tasks = result["data"].get("tasks", [])
        return ToolResponse(
            success=True,
            data={
                "tasks": tasks,
                "total_count": len(tasks),
                "limit": request.limit,
                "offset": request.offset
            },
            message=f"Found {len(tasks)} task(s)"
        )
    else:
        return ToolResponse(
            success=False,
            error=result.get("error"),
            message="Failed to list tasks"
        )


@app.post("/tools/complete_task", response_model=ToolResponse)
async def complete_task(request: CompleteTaskRequest):
    """
    Mark a task as completed.
    
    Calls the backend /api/tasks/{id}/complete endpoint.
    """
    logger.info("complete_task called", user_id=request.user_id, task_id=request.task_id)
    
    result = await call_backend_api(
        endpoint=f"/api/tasks/{request.task_id}",
        method="PATCH",
        jwt_token=request.jwt_token,
        data={"status": "completed"}
    )
    
    if result["success"]:
        return ToolResponse(
            success=True,
            data=result["data"],
            message=f"Task {request.task_id} marked as completed!"
        )
    else:
        return ToolResponse(
            success=False,
            error=result.get("error"),
            message=f"Failed to complete task {request.task_id}"
        )


@app.post("/tools/delete_task", response_model=ToolResponse)
async def delete_task(request: DeleteTaskRequest):
    """
    Delete a task.
    
    Calls the backend /api/tasks/{id} DELETE endpoint.
    """
    logger.info("delete_task called", user_id=request.user_id, task_id=request.task_id)
    
    result = await call_backend_api(
        endpoint=f"/api/tasks/{request.task_id}",
        method="DELETE",
        jwt_token=request.jwt_token
    )
    
    if result["success"]:
        return ToolResponse(
            success=True,
            data={"task_id": request.task_id},
            message=f"Task {request.task_id} deleted successfully!"
        )
    else:
        return ToolResponse(
            success=False,
            error=result.get("error"),
            message=f"Failed to delete task {request.task_id}"
        )


@app.post("/tools/update_task", response_model=ToolResponse)
async def update_task(request: UpdateTaskRequest):
    """
    Update an existing task.
    
    Calls the backend /api/tasks/{id} PATCH endpoint.
    """
    logger.info("update_task called", user_id=request.user_id, task_id=request.task_id)
    
    update_data = {}
    if request.title:
        update_data["title"] = request.title
    if request.description:
        update_data["description"] = request.description
    if request.priority:
        update_data["priority"] = request.priority
    if request.due_date:
        update_data["due_date"] = request.due_date
    if request.tags is not None:
        update_data["tags"] = request.tags
    
    if not update_data:
        return ToolResponse(
            success=False,
            error={"code": "NO_UPDATES", "message": "No fields to update"},
            message="Please provide at least one field to update"
        )
    
    result = await call_backend_api(
        endpoint=f"/api/tasks/{request.task_id}",
        method="PATCH",
        jwt_token=request.jwt_token,
        data=update_data
    )
    
    if result["success"]:
        return ToolResponse(
            success=True,
            data=result["data"],
            message=f"Task {request.task_id} updated successfully!"
        )
    else:
        return ToolResponse(
            success=False,
            error=result.get("error"),
            message=f"Failed to update task {request.task_id}"
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "MCP HTTP Server",
        "version": "1.0.0",
        "tools": ["add_task", "list_tasks", "complete_task", "delete_task", "update_task"]
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    try:
        # Check if we can connect to the backend
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BACKEND_URL}/health/health")
            backend_healthy = response.status_code == 200
    except Exception:
        backend_healthy = False

    # Check required environment variables
    required_vars = ["BACKEND_URL", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    is_ready = backend_healthy and len(missing_vars) == 0

    return {
        "status": "ready" if is_ready else "not_ready",
        "service": "MCP HTTP Server",
        "version": "1.0.0",
        "backend_healthy": backend_healthy,
        "missing_env_vars": missing_vars,
        "checks": {
            "backend": "healthy" if backend_healthy else "unhealthy",
            "environment": "healthy" if len(missing_vars) == 0 else "missing_variables"
        }
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "MCP HTTP Server",
        "version": "1.0.0",
        "description": "HTTP wrapper for MCP tools",
        "endpoints": {
            "add_task": "POST /tools/add_task",
            "list_tasks": "POST /tools/list_tasks",
            "complete_task": "POST /tools/complete_task",
            "delete_task": "POST /tools/delete_task",
            "update_task": "POST /tools/update_task",
            "health": "GET /health"
        }
    }


def signal_handler(signum, frame):
    """Handle graceful shutdown signals"""
    print(f"\n🛑 Received signal {signum}. Shutting down MCP HTTP Server gracefully...")
    sys.exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("MCP_HTTP_PORT", 8001))

    print(f"🚀 Starting MCP HTTP Server on port {port}")
    print(f"📡 Backend URL: {BACKEND_URL}")
    print(f"🔧 Available tools: add_task, list_tasks, complete_task, delete_task, update_task")

    uvicorn.run(
        "http_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info",
        access_log=True
    )
