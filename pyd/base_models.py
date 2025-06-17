from pydantic import BaseModel, EmailStr, Field, conint, confloat
from typing import List, Optional
from datetime import datetime

class RoleBase(BaseModel):
    name: str

class RoleRead(RoleBase):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserUpdate(UserBase):
    password: Optional[str] = None
    role_id: Optional[int] = None 

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str

class CategoryRead(CategoryBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    remaining_stock: Optional[float] = None
    category_id: int = Field(..., gt=0)

class ProductRead(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class OrderStatusBase(BaseModel):
    name: str

class OrderStatusRead(OrderStatusBase):
    id: int

    class Config:
        from_attributes = True

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1, gt=0)
    price_at_purchase: int = Field(..., ge=0)

    class Config:
        from_attributes = True
        
class OrderBase(BaseModel):
    id: int
    user_id: int
    status_id: int
    total_amount: float
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemBase]
    
    class Config:
        from_attributes = True
        
class OrderRead(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
class ReviewBase(BaseModel):
    product_id: int
    user_id: int
    rating: int = Field(..., ge=1, le=5)
    text: Optional[str] = None

class ReviewRead(ReviewBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReviewUpdate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    text: Optional[str] = None
