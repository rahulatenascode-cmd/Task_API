from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4

class Permission(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True)
