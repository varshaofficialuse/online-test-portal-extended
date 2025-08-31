from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import SignupIn, LoginIn, TokenOut
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.models.role_enum import UserRole
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials






router = APIRouter()
auth_scheme = HTTPBearer()


def get_current_user(token: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> int:
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    


def admin_required(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

    
@router.post("/signup")
def signup(payload: SignupIn, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.STUDENT
    )

    if user.role.lower() == "admin":
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to signup as Admin"
        )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully"}




@router.get("/me")
def get_me(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }


@router.post("/login", response_model=dict)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(sub=str(user.id), minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_access_token(sub=str(user.id), minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES, secret=settings.REFRESH_SECRET_KEY)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh", response_model=dict)
def refresh_token(token: HTTPAuthorizationCredentials = Depends(auth_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token.credentials, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Issue new access token
    access_token = create_access_token(sub=str(user.id), minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {"access_token": access_token,
            "refresh_token": token.credentials  # re-use same refresh token
}






@router.post("/admin/create/")
def create_admin(
    user_data: SignupIn,
    current_user_id: int = Depends(get_current_user),  
    db: Session = Depends(get_db)
):
    current_user = db.query(User).filter(User.id == current_user_id).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")

    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Only superadmin can create admins")

    exists = db.query(User).filter(User.email == user_data.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_admin = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=UserRole.ADMIN
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {
        "message": "Admin created successfully",
        "name": new_admin.name,
        "email": new_admin.email,
        "role": new_admin.role
    }


