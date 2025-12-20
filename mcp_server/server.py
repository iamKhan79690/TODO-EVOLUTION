"""
Simplified MCP Server for TODO-Evolution Phase III
Works with fastmcp 2.x API
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

from typing import Dict, Any, Optional, List
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Create FastAPI app for HTTP interface
app = FastAPI(
    title="MCP Task Server",
    version="1.0.0",
    description="MCP server for TODO-Evolution task management"
)


# Request/Response models
class AddTaskRequest(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    jwt_token: str


class ListTasksRequest(BaseModel):
    user_id: int
    status: Optional[str] = "all"
    jwt_token: str


class TaskOperationRequest(BaseModel):
    user_id: int
    task_id: int
    jwt_token: str


class UpdateTaskRequest(BaseModel):
    user_id: int
    task_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    jwt_token: str


class ToolResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None


# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "MCP Task Server", "version": "1.0.0"}


# Tool endpoints
@app.post("/tools/add_task", response_model=ToolResponse)
async def add_task(request: AddTaskRequest):
    """Add a new task via MCP tool."""
    try:
        # Import here to avoid circular imports
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/tasks",
                json={
                    "title": request.title,
                    "description": request.description
                },
                headers={"Authorization": f"Bearer {request.jwt_token}"}
            )
            
            if response.status_code == 200:
                task_data = response.json()
                return ToolResponse(
                    success=True,
                    data={"task_id": task_data.get("id"), "status": "created", "title": request.title},
                    message=f"Task '{request.title}' created successfully"
                )
            else:
                return ToolResponse(success=False, error=f"HTTP {response.status_code}")
                
    except Exception as e:
        return ToolResponse(success=False, error=str(e))


@app.post("/tools/list_tasks", response_model=ToolResponse)
async def list_tasks(request: ListTasksRequest):
    """List tasks via MCP tool."""
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/api/v1/tasks",
                headers={"Authorization": f"Bearer {request.jwt_token}"}
            )
            
            if response.status_code == 200:
                tasks = response.json()
                
                # Filter by status if needed
                if request.status == "completed":
                    tasks = [t for t in tasks if t.get("is_completed")]
                elif request.status == "pending":
                    tasks = [t for t in tasks if not t.get("is_completed")]
                
                return ToolResponse(
                    success=True,
                    data={"tasks": tasks, "count": len(tasks)},
                    message=f"Found {len(tasks)} tasks"
                )
            else:
                return ToolResponse(success=False, error=f"HTTP {response.status_code}")
                
    except Exception as e:
        return ToolResponse(success=False, error=str(e))


@app.post("/tools/complete_task", response_model=ToolResponse)
async def complete_task(request: TaskOperationRequest):
    """Mark a task as complete via MCP tool."""
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"http://localhost:8000/api/v1/tasks/{request.task_id}",
                json={"is_completed": True},
                headers={"Authorization": f"Bearer {request.jwt_token}"}
            )
            
            if response.status_code == 200:
                return ToolResponse(
                    success=True,
                    data={"task_id": request.task_id, "status": "completed"},
                    message=f"Task {request.task_id} marked as complete"
                )
            else:
                return ToolResponse(success=False, error=f"HTTP {response.status_code}")
                
    except Exception as e:
        return ToolResponse(success=False, error=str(e))


@app.post("/tools/delete_task", response_model=ToolResponse)
async def delete_task(request: TaskOperationRequest):
    """Delete a task via MCP tool."""
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"http://localhost:8000/api/v1/tasks/{request.task_id}",
                headers={"Authorization": f"Bearer {request.jwt_token}"}
            )
            
            if response.status_code in [200, 204]:
                return ToolResponse(
                    success=True,
                    data={"task_id": request.task_id, "status": "deleted"},
                    message=f"Task {request.task_id} deleted"
                )
            else:
                return ToolResponse(success=False, error=f"HTTP {response.status_code}")
                
    except Exception as e:
        return ToolResponse(success=False, error=str(e))


@app.post("/tools/update_task", response_model=ToolResponse)
async def update_task(request: UpdateTaskRequest):
    """Update a task via MCP tool."""
    try:
        import httpx
        
        update_data = {}
        if request.title:
            update_data["title"] = request.title
        if request.description:
            update_data["description"] = request.description
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"http://localhost:8000/api/v1/tasks/{request.task_id}",
                json=update_data,
                headers={"Authorization": f"Bearer {request.jwt_token}"}
            )
            
            if response.status_code == 200:
                return ToolResponse(
                    success=True,
                    data={"task_id": request.task_id, "status": "updated", "title": request.title},
                    message=f"Task {request.task_id} updated"
                )
            else:
                return ToolResponse(success=False, error=f"HTTP {response.status_code}")
                
    except Exception as e:
        return ToolResponse(success=False, error=str(e))


if __name__ == "__main__":
    port = int(os.getenv("MCP_SERVER_PORT", 8001))
    print(f"Starting MCP Task Server on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
