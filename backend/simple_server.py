from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

app = FastAPI(title="Todo Evolution API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data storage
tasks_db = []

# Pydantic models
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[str] = None
    tags: Optional[List[str]] = []

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    tags: Optional[List[str]] = None

# API Routes
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/tasks", response_model=List[TaskResponse])
async def get_tasks():
    return tasks_db

@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    new_task = TaskResponse(
        id=str(uuid.uuid4()),
        title=task.title,
        description=task.description,
        status="pending",
        priority=task.priority,
        due_date=task.due_date,
        tags=task.tags or [],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    tasks_db.append(new_task)
    return new_task

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    task = next((t for t in tasks_db if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.patch("/api/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_update: TaskUpdate):
    task_index = next((i for i, t in enumerate(tasks_db) if t.id == task_id), None)
    if task_index is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks_db[task_index]

    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status is not None:
        task.status = task_update.status
    if task_update.priority is not None:
        task.priority = task_update.priority
    if task_update.due_date is not None:
        task.due_date = task_update.due_date
    if task_update.tags is not None:
        task.tags = task_update.tags

    task.updated_at = datetime.now()
    return task

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    task_index = next((i for i, t in enumerate(tasks_db) if t.id == task_id), None)
    if task_index is None:
        raise HTTPException(status_code=404, detail="Task not found")

    tasks_db.pop(task_index)
    return {"message": "Task deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)