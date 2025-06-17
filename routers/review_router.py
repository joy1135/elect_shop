from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from auth import get_current_user
from database import get_db
import models as m
import pyd
from datetime import datetime, UTC

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/", response_model=pyd.ReviewRead)
def create_review(
    review_data: pyd.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user)
):
    existing = db.query(m.Review).filter_by(
        product_id=review_data.product_id,
        user_id=current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Вы уже оставили отзыв на этот товар")

    new_review = m.Review(
        **review_data.dict(),
        user_id=current_user.id
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@router.get("/product/{product_id}", response_model=List[pyd.ReviewRead])
def get_reviews_by_product(product_id: int, db: Session = Depends(get_db)):
    reviews = db.query(m.Review).filter(m.Review.product_id == product_id).all()
    return reviews

@router.put("/{review_id}", response_model=pyd.ReviewRead)
def update_review(
    review_id: int,
    review_data: pyd.ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user)
):
    review = db.query(m.Review).get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    if current_user.role_id not in (2, 3) and review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для редактирования этого отзыва")
    for key, value in review_data.dict().items():
        setattr(review, key, value)

    review.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(review)
    return review

@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user)
):
    review = db.query(m.Review).get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    if current_user.role_id not in (2, 3) and review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для удаления этого отзыва")

    db.delete(review)
    db.commit()
    return {"detail": "Отзыв успешно удалён"}
