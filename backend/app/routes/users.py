# backend/app/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database.config import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate

# Buat router
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# GET all users
@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {
        "total": len(users),
        "users": [user.to_dict() for user in users]
    }

# GET user by ID
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return {"user": user.to_dict()}

# GET users by role
@router.get("/role/{role}")
def get_users_by_role(role: str, db: Session = Depends(get_db)):
    if role not in ['admin', 'user']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'admin' or 'user'"
        )
    users = db.query(User).filter(User.role == role).all()
    return {
        "role": role,
        "total": len(users),
        "users": [user.to_dict() for user in users]
    }

# ====================== POST USER  ====================== #
@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    
    - **name**: User's full name
    - **email**: Must be unique
    - **password**: Minimum 6 characters
    - **role**: 'admin' or 'user' (default: 'user')
    - **parent_id**: Optional, for user hierarchy
    - **is_active**: Default is True
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    db_user = User(
        name=user.name,
        email=user.email,
        password=user.password,  # TODO: Hash password later
        role=user.role,
        parent_id=user.parent_id,
        is_active=user.is_active
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "message": "User created successfully",
        "user": db_user.to_dict()
    }