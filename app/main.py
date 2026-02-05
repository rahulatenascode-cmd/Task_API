from fastapi import FastAPI
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.routers import auth, users, tasks
from app.models import user, task, role, permission, role_permission

app = FastAPI(title="FastAPI Task Manager 🚀")

# CORS middleware (allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all tables
SQLModel.metadata.create_all(engine)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

# Root endpoint
@app.get("/")
def root():
    return {"message": "FastAPI Task Manager is running 🚀"}

# Optional: startup event to initialize default roles & permissions
@app.on_event("startup")
def init_roles_permissions():
    from sqlmodel import Session, select
    from app.models.role import Role
    from app.models.permission import Permission
    from app.models.role_permission import RoleHasPermission

    with Session(engine) as session:
        # Create default roles
        for role_name in ["admin", "user"]:
            if not session.exec(select(Role).where(Role.name == role_name)).first():
                session.add(Role(name=role_name))
        # Create default permissions
        default_permissions = ["create_user", "view_user", "update_user", "delete_user"]
        for perm_name in default_permissions:
            if not session.exec(select(Permission).where(Permission.name == perm_name)).first():
                session.add(Permission(name=perm_name))
        session.commit()
