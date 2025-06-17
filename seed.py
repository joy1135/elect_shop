from datetime import datetime, UTC
from sqlalchemy.orm import Session
from database import engine
import models as m 
import bcrypt

m.Base.metadata.drop_all(bind=engine)
m.Base.metadata.create_all(bind=engine)

def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

with Session(bind=engine) as session:
    now = datetime.now(UTC)

    admin_role = m.Role(name="Админ")
    user_role = m.Role(name="Покупатель")
    manager_role = m.Role(name="Менеджер")
    
    status_new = m.OrderStatus(name="новый")
    status_processing = m.OrderStatus(name="в обработке")
    status_sent = m.OrderStatus(name="отправлен")
    status_delivered = m.OrderStatus(name="доставлен")
    status_cancelled = m.OrderStatus(name="отменён")

    phone = m.Category(name="Телефон",created_at=now)
    tv = m.Category(name="ТВ",created_at=now)

    admin_user = m.User(
        username="Админ",
        email="admin@example.com",
        password=hash_password("admin123"),
        role=admin_role,
        created_at=now
    )
    regular_user = m.User(
        username="Покупатель",
        email="user@example.com",
        password=hash_password("user123"),
        role=user_role,
        created_at=now
    )
    man_user = m.User(
        username="Менеджер",
        email="manager@example.com",
        password=hash_password("manag123"),
        role=manager_role,
        created_at=now
    )

    product1 = m.Product(
        name="Смартфон Galaxy",
        price=30000,
        description="Современный смартфон",
        remaining_stock=10,
        category=phone,
        created_at=now
    )

    product2 = m.Product(
        name="Toshiba 5000",
        price=25000,
        description="Лучшая технология экрана",
        remaining_stock=50,
        category=tv,
        created_at=now
    )

    session.add_all([
         user_role, manager_role, admin_role,
        status_new, status_processing, status_sent, status_delivered, status_cancelled,
        phone, tv,
        admin_user, regular_user, man_user,
        product1, product2
    ])

    session.commit()

    order1 = m.Order(
    user=regular_user,
    status=status_new,
    created_at=now,
    updated_at=now
)

order1_item1 = m.OrderItem(
    product=product1,
    quantity=2,
    price_at_purchase=30000
)
order1_item2 = m.OrderItem(
    product=product2,
    quantity=1,
    price_at_purchase=25000
)

order1.items = [order1_item1, order1_item2]
order1.total_amount = sum(item.quantity * item.price_at_purchase for item in order1.items)

order2 = m.Order(
    user=man_user,
    status=status_processing,
    created_at=now,
    updated_at=now
)

order2_item = m.OrderItem(
    product=product2,
    quantity=3,
    price_at_purchase=25000
)

order2.items = [order2_item]
order2.total_amount = sum(item.quantity * item.price_at_purchase for item in order2.items)

session.add_all([order1, order2])
session.commit()

