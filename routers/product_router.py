from fastapi import APIRouter, HTTPException, Depends, Query, status
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
import models as m
import pyd
from typing import List, Optional
from auth import get_current_user

router = APIRouter(
    prefix="/product",
    tags=["product"],
)

@router.get("/products", response_model=List[pyd.ProductBase])
def get_all_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    name: str = Query(None),
    category_id: int = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0)
):
    query = db.query(m.Product)

    if name:
        search = f"%{name.lower()}%"
        query = query.filter(func.lower(m.Product.name).like(search))

    if category_id is not None:
        query = query.filter(m.Product.category_id == category_id)

    if min_price is not None:
        query = query.filter(m.Product.price >= min_price)

    if max_price is not None:
        query = query.filter(m.Product.price <= max_price)

    offset = (page - 1) * limit
    return query.offset(offset).limit(limit).all()

@router.get("/{product_id}", response_model=pyd.ProductBase)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(m.Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product

@router.post("/create", response_model=pyd.ProductBase)
def create_product(
    product_data: pyd.ProductCreate,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user)
):
    if current_user.role_id not in (2, 3):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания продукта"
        )

    category = db.query(m.Category).filter(m.Category.id == product_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категория с таким ID не найдена"
        )

    product = m.Product(**product_data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/update/{product_id}", response_model=pyd.ProductBase)
def update_product(
    product_id: int, product_data: pyd.ProductCreate, 
    db: Session = Depends(get_db), 
    current_user: m.User = Depends(get_current_user)
    ):
    
    if current_user.role_id not in (2, 3):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания продукта"
        )
    
    if product_data.category_id == 0:
        raise HTTPException(status_code=400, detail="category_id не может быть 0")    
    
    product = db.query(m.Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    for key, value in product_data.dict().items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/delete/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: m.User = Depends(get_current_user)):
    
    if current_user.role_id not in (2, 3):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания продукта"
        )
        
    product = db.query(m.Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    db.delete(product)
    db.commit()
    return {"detail": "Товар успешно удалён"}

