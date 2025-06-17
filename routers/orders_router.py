from fastapi import APIRouter, HTTPException, Depends, Query, status
from database import get_db
from sqlalchemy.orm import Session
import models as m
import pyd
from typing import List
from auth import get_current_user

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

@router.get("/", response_model=List[pyd.OrderBase])
def get_all_orders(
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
):
    if current_user.role_id not in (2, 3):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания продукта"
        )
    query = db.query(m.Order)

    offset = (page - 1) * limit
    return query.offset(offset).limit(limit).all()

@router.get("/user_orders", response_model=List[pyd.OrderBase])
def get_all_orders_user(
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
):
    query = db.query(m.Order).filter(m.Order.user_id == current_user.id)

    offset = (page - 1) * limit
    return query.offset(offset).limit(limit).all()

@router.get("/{order_id}", response_model=pyd.OrderBase)
def get_order(
    order_id: int, 
    db: Session = Depends(get_db), 
    current_user: m.User = Depends(get_current_user)
):
    order = db.query(m.Order).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    if current_user.role_id == 1 and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому заказу")

    return order

@router.post("/create", response_model=pyd.OrderBase)
def create_order(
    order_data: pyd.OrderCreate,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user)
):
    if not order_data.items:
        raise HTTPException(status_code=400, detail="Нельзя создать заказ без товаров")

    total = 0
    order_items = []

    for item in order_data.items:
        product = db.query(m.Product).filter(m.Product.id == item.product_id).with_for_update().first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Товар ID {item.product_id} не найден")

        if item.quantity > product.remaining_stock:
            raise HTTPException(
                status_code=400,
                detail=f"Недостаточно товара '{product.name}' на складе. Осталось: {product.remaining_stock}"
            )

        product.remaining_stock -= item.quantity
        
        total += item.quantity * float(product.price)
        order_items.append(
            m.OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=product.price
            )
        )

    order = m.Order(
        user_id=current_user.id,
        status_id=order_data.status_id,
        total_amount=total,
        items=order_items
    )

    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@router.put("/update-status/{order_id}", response_model=pyd.OrderBase)
def update_order_status(
    order_id: int,
    status_id: int,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user)
):
    if current_user.role_id not in (2, 3):
        raise HTTPException(status_code=403, detail="Недостаточно прав для изменения статуса")

    order = db.query(m.Order).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    status = db.query(m.OrderStatus).get(status_id)
    if not status:
        raise HTTPException(status_code=400, detail="Статус не существует")

    order.status_id = status_id
    db.commit()
    db.refresh(order)
    return order

@router.put("/update-items/{order_id}", response_model=pyd.OrderBase)
def update_order_items(
    order_id: int,
    items_data: pyd.OrderItemsUpdate,  # создадим ниже
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user)
):
    if current_user.role_id not in (2, 3):
        raise HTTPException(status_code=403, detail="Недостаточно прав для изменения состава заказа")

    order = db.query(m.Order).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    for item in order.items:
        product = db.query(m.Product).get(item.product_id)
        if product:
            product.remaining_stock += item.quantity

    db.query(m.OrderItem).filter(m.OrderItem.order_id == order.id).delete()

    new_items = []
    total = 0
    for item in items_data.items:
        product = db.query(m.Product).filter(m.Product.id == item.product_id).with_for_update().first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Товар ID {item.product_id} не найден")
        if item.quantity > product.remaining_stock:
            raise HTTPException(status_code=400, detail=f"Недостаточно товара '{product.name}' на складе")

        product.remaining_stock -= item.quantity
        total += item.quantity * float(product.price)

        new_items.append(
            m.OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=product.price,
                order_id=order.id
            )
        )

    order.total_amount = total
    order.items = new_items

    db.commit()
    db.refresh(order)
    return order

@router.delete("/delete/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user)
):
    order = db.query(m.Order).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    if current_user.role_id == 1:
        if order.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Вы не можете удалить этот заказ")
        if order.status.name.lower() != "новый":
            raise HTTPException(status_code=400, detail="Удалять можно только заказы со статусом 'новый'")

    for item in order.items:
        product = db.query(m.Product).get(item.product_id)
        if product:
            product.remaining_stock += item.quantity

    db.delete(order)
    db.commit()

    return {"detail": "Заказ успешно удалён"}
