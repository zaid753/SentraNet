from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.api.database import get_db
from backend.api.models import User, Workspace
from backend.api.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from backend.api.auth import get_password_hash, verify_password, create_access_token, get_current_user, get_current_workspace

router = APIRouter()

@router.post("/signup", response_model=Token)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system."
        )
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        name=user_in.name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    workspace = Workspace(
        name=user_in.workspace_name,
        owner_id=user.id
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer", "workspace_id": workspace.id}

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    workspace = db.query(Workspace).filter(Workspace.owner_id == user.id).first()
    if not workspace:
        raise HTTPException(status_code=400, detail="User has no workspace")

    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer", "workspace_id": workspace.id}

@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace)
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "workspace_id": workspace.id,
        "workspace_name": workspace.name,
        "onboarded": True  # simplified for now, as Phase 6 requested persisting it conceptually. We'll treat signup as onboarding.
    }
