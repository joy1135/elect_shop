from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from sqlalchemy.orm import Session
import models as m
import pyd
from auth import authenticate_user, create_access_token, get_current_user, hash_password
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.post("/register")
def register_user(user: pyd.UserCreate, db: Session = Depends(get_db)):
    email_user = db.query(m.User).filter(m.User.email == user.email).first()
    if email_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    name_user = db.query(m.User).filter(m.User.username == user.username).first()
    if name_user:
        raise HTTPException(status_code=400, detail="Username уже зарегистрирован")
    
    
    hashed_pwd = hash_password(user.password)
    new_user = m.User(
        username=user.username,
        email=user.email,
        password=hashed_pwd,
        role_id=1,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "Пользователь успешно создан"}

@router.get("/me")
def get_me(current_user: m.User = Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email}