from typing import List, Optional
from auth import hash_password
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import func
from database import get_db
from sqlalchemy.orm import Session
import models as m
import pyd
from auth import authenticate_user, create_access_token, get_current_user, hash_password

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

@router.get("/", response_model=List[pyd.UserRead])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    username: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    role_id: Optional[int] = Query(None)
):
    if current_user.role_id != 3:
        raise HTTPException(status_code=403, detail="Только администратор может просматривать всех пользователей")

    query = db.query(m.User)

    if username:
        query = query.filter(func.lower(m.User.username).like(f"%{username.lower()}%"))
    if email:
        query = query.filter(func.lower(m.User.email).like(f"%{email.lower()}%"))
    if role_id:
        query = query.filter(m.User.role_id == role_id)

    offset = (page - 1) * limit
    users = query.offset(offset).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=pyd.UserRead)
def get_user_by_id(user_id: int, db: Session = Depends(get_db),  current_user: m.User = Depends(get_current_user)):
    if current_user.role_id != 3:
        raise HTTPException(status_code=403, detail="Только администратор может просматривать всех пользователей")
    user = db.query(m.User).filter(m.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@router.put("/{user_id}", response_model=pyd.UserRead)
def update_user(
    user_id: int,
    data: pyd.UserUpdate,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user)
):
    if current_user.role_id != 3:
        raise HTTPException(status_code=403, detail="Только администратор может редактировать пользователей")

    user = db.query(m.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if data.username:
        user.username = data.username
    if data.email:
        user.email = data.email
    if data.password:
        user.password = hash_password(data.password)
    if data.role_id is not None:
        user.role_id = data.role_id

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user)
):
    if current_user.role_id != 3:
        raise HTTPException(status_code=403, detail="Только администратор может удалять пользователей")

    user = db.query(m.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.orders:
        raise HTTPException(status_code=400, detail="Нельзя удалить пользователя с заказами")


    db.delete(user)
    db.commit()
    return {"detail": "Пользователь успешно удалён"}
