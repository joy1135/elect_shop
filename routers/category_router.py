from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from sqlalchemy.orm import Session
import models as m
import pyd
from typing import List
from auth import get_current_user

router = APIRouter(
    prefix="/category",
    tags=["category"],
)

@router.get("/", response_model=List[pyd.CategoryRead])
def get_all_categories(db: Session = Depends(get_db)):
    return db.query(m.Category).all()

@router.post("/", response_model=pyd.CategoryRead)
def create_category(
    data: pyd.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user)
):
    if current_user.role_id != 3:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    existing = db.query(m.Category).filter_by(name=data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Такая категория уже существует")

    category = m.Category(**data.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.put("/{category_id}", response_model=pyd.CategoryRead)
def update_category(
    category_id: int,
    data: pyd.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user)
):
    if current_user.role_id != 3: 
        raise HTTPException(status_code=403, detail="Только администратор может редактировать категории")

    category = db.query(m.Category).get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    category.name = data.name
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user)
):
    if current_user.role_id != 3:
        raise HTTPException(status_code=403, detail="Только администратор может удалить категорию")

    category = db.query(m.Category).get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    db.delete(category)
    db.commit()
    return {"detail": "Категория успешно удалена"}