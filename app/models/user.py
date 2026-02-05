from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    role_id: UUID | None = Field(default=None, foreign_key="role.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
