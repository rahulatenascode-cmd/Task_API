from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from uuid import UUID
from jose import jwt, JWTError

from app.database import get_session
from app.models.user import User
from app.models.permission import Permission
from app.models.role_permission import RoleHasPermission
from app.core.security import SECRET_KEY, ALGORITHM

security = HTTPBearer(auto_error=True)

# Dependency: Get the current logged-in user from JWT
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str | None = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        user_id = UUID(user_id_str)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# Dependency: Require a specific permission
def require_permission(permission_name: str):
    def checker(
        user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
    ):
        stmt = (
            select(Permission)
            .join(RoleHasPermission)
            .where(
                RoleHasPermission.role_id == user.role_id,
                Permission.name == permission_name
            )
        )
        if not session.exec(stmt).first():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user
    return checker
