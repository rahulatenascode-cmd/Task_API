from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from typing import List

from app.database import get_session
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.core.deps import get_current_user

router = APIRouter(tags=["Tasks"])


@router.post("/", response_model=TaskResponse)
def create_task(
    data: TaskCreate,
    session: Session = Depends(get_session),
    user = Depends(get_current_user)
):
    task = Task(**data.dict(), owner_id=user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    status: str | None = Query(
        None,
        description="Filter by status (comma-separated): pending, in_progress, completed"
    ),
    priority: str | None = Query(
        None,
        description="Filter by priority (comma-separated): low, medium, high"
    ),
    limit: int = Query(10, ge=1, le=100, description="Number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    session: Session = Depends(get_session),
    user = Depends(get_current_user)
):
    stmt = select(Task).where(Task.owner_id == user.id)

    # Filter status
    if status:
        status_list = [
            s.strip() for s in status.split(",") 
            if s.strip() in TaskStatus._value2member_map_
        ]
        if status_list:
            stmt = stmt.where(Task.status.in_(status_list))

    # Filter priority
    if priority:
        priority_list = [
            p.strip() for p in priority.split(",") 
            if p.strip() in TaskPriority._value2member_map_
        ]
        if priority_list:
            stmt = stmt.where(Task.priority.in_(priority_list))

    tasks = session.exec(stmt.offset(offset).limit(limit)).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, session: Session = Depends(get_session), user=Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: UUID, data: TaskUpdate, session: Session = Depends(get_session), user=Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    if data.status:
        task.status = data.status
    if data.priority:
        task.priority = data.priority

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: UUID, session: Session = Depends(get_session), user=Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"message": "Task deleted"}
