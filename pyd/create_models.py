from pydantic import BaseModel, validator, EmailStr, Field, EmailStr, field_validator
from typing import List, Optional
import re

from pyd.base_models import OrderItemBase

class RoleCreate(BaseModel):
    name: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль должен быть больше 8 символов")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v

class CategoryCreate(BaseModel):
    name: str

class ProductCreate(BaseModel):
    name: str
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    description: Optional[str] = None
    remaining_stock: Optional[float] = None
    category_id: int  # Сделали обязательным

    @validator("price")
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

class OrderStatusCreate(BaseModel):
    name: str

class OrderCreate(BaseModel):
    user_id: int
    status_id: int
    total_amount: float
    
class OrderItemCreate(OrderItemBase):
    pass

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    status_id: Optional[int] = 1

class ReviewCreate(BaseModel):
    product_id: int
    user_id: int
    rating: int = Field(..., ge=1, le=5)
    text: Optional[str] = None

class OrderItemInput(BaseModel):
    product_id: int
    quantity: int

class OrderItemsUpdate(BaseModel):
    items: List[OrderItemInput]