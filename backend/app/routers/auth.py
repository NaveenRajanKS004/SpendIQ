from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import os

from ..database import SessionLocal
from .. import models, schemas
from ..security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)


# This router handles all authentication and user profile operations:
# - registration & login
# - profile retrieval & updates
# - profile picture upload
# - password management
router = APIRouter()


# =========================
# DATABASE DEPENDENCY
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# REGISTER
# =========================

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # Check if email is already registered
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password before storing
    hashed_pw = hash_password(user.password)

    # Create new user record
    new_user = models.User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        date_of_birth=user.date_of_birth,
        hashed_password=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================
# LOGIN
# =========================

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # Fetch user using email (OAuth uses "username" field)
    user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    # Validate user existence
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # Generate JWT token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30),
    )

    return {"access_token": access_token, "token_type": "bearer"}


# =========================
# GET CURRENT USER
# =========================

@router.get("/me", response_model=schemas.UserResponse)
def read_current_user(
    current_user: models.User = Depends(get_current_user)
):
    return current_user


# =========================
# UPDATE PROFILE
# =========================

@router.put("/profile")
def update_profile(
    update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    # Re-fetch user in current DB session (avoids session mismatch issues)
    user = db.query(models.User).filter(
        models.User.id == current_user.id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only provided fields
    if update.name is not None:
        user.name = update.name

    if update.phone is not None:
        user.phone = update.phone

    if update.date_of_birth is not None:
        user.date_of_birth = update.date_of_birth

    db.commit()
    db.refresh(user)

    return {"message": "Profile updated successfully"}


# =========================
# UPLOAD PROFILE PICTURE
# =========================

@router.post("/profile/upload-picture")
def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    # Fetch user in current session
    user = db.query(models.User).filter(
        models.User.id == current_user.id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Ensure upload directory exists
    upload_dir = "app/static/profile_pics"
    os.makedirs(upload_dir, exist_ok=True)

    # Save file with user-specific naming
    file_path = f"{upload_dir}/{user.id}_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Store accessible path in DB
    user.profile_picture = f"/static/profile_pics/{user.id}_{file.filename}"

    db.commit()

    return {"profile_picture": user.profile_picture}


# =========================
# CHANGE PASSWORD
# =========================

@router.put("/change-password")
def change_password(
    data: schemas.ChangePassword,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    # Fetch user in current session
    user = db.query(models.User).filter(
        models.User.id == current_user.id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify old password before allowing change
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    # Update to new hashed password
    user.hashed_password = hash_password(data.new_password)

    db.commit()

    return {"message": "Password updated successfully"}