from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User
from app.schemas.auth import RegisterSchema, LoginSchema, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(tags=["Auth"])

@router.post("/register", summary="Register a new user")
def register(data: RegisterSchema, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User registered", "user_id": str(user.id)}

@router.post("/login", response_model=TokenResponse, summary="Login and get access token")
def login(data: LoginSchema, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
