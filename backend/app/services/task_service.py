from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import DashboardStats, TaskCreate, TaskUpdate


def list_tasks(db: Session, user_id: int, search: str | None = None) -> list[Task]:
    stmt = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(or_(Task.title.ilike(pattern), Task.description.ilike(pattern)))
    return list(db.scalars(stmt).all())


def create_task(db: Session, user_id: int, payload: TaskCreate) -> Task:
    task = Task(user_id=user_id, **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_user_task(db: Session, user_id: int, task_id: int) -> Task | None:
    return db.scalar(select(Task).where(Task.user_id == user_id, Task.id == task_id))


def update_task(db: Session, task: Task, payload: TaskUpdate) -> Task:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


def dashboard_stats(db: Session, user_id: int) -> DashboardStats:
    total = db.scalar(select(func.count(Task.id)).where(Task.user_id == user_id)) or 0
    completed = (
        db.scalar(select(func.count(Task.id)).where(Task.user_id == user_id, Task.status == "completed")) or 0
    )
    pending = total - completed
    percentage = round((completed / total) * 100, 2) if total else 0
    return DashboardStats(
        total_tasks=total,
        completed_tasks=completed,
        pending_tasks=pending,
        completion_percentage=percentage,
    )
