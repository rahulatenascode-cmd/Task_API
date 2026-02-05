from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role_id: Optional[UUID] = None  # Only admin can assign role

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role_id: Optional[UUID] = None

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True
