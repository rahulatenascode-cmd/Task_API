from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from uuid import UUID

from app.database import get_session
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.deps import require_permission
from app.core.security import hash_password

router = APIRouter(tags=["Users"])


@router.post("/", response_model=UserResponse, dependencies=[Depends(require_permission("create_user"))])
def create_user(data: UserCreate, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == data.email)).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role_id=data.role_id
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/", response_model=list[UserResponse], dependencies=[Depends(require_permission("view_user"))])
def list_users(
    role: str | None = Query(default=None, description="Filter by role name"),
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session)
):
    stmt = select(User)

    if role:
        stmt = stmt.join(Role, isouter=True).where(Role.name == role)

    stmt = stmt.offset(offset).limit(limit)
    return session.exec(stmt).all()


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_permission("view_user"))])
def get_user(user_id: str, session: Session = Depends(get_session)):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user = session.get(User, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_permission("update_user"))])
def update_user(user_id: str, data: UserUpdate, session: Session = Depends(get_session)):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user = session.get(User, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.email:
        existing = session.exec(select(User).where(User.email == data.email, User.id != user_uuid)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = data.email

    if data.role_id:
        user.role_id = data.role_id

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}", dependencies=[Depends(require_permission("delete_user"))])
def delete_user(user_id: str, session: Session = Depends(get_session)):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user = session.get(User, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
    return {"message": "User deleted"}

