from sqlmodel import SQLModel, Field
from uuid import UUID

class RoleHasPermission(SQLModel, table=True):
    role_id: UUID = Field(foreign_key="role.id", primary_key=True)
    permission_id: UUID = Field(foreign_key="permission.id", primary_key=True)
