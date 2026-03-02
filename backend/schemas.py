from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DealBase(BaseModel):
    title: str
    price: float
    shipping_fee: Optional[float] = 0.0
    mall: Optional[str] = None
    source: str
    url: str
    likes: Optional[int] = 0
    comments: Optional[int] = 0
    is_ended: Optional[bool] = False

class DealCreate(DealBase):
    pass

class Deal(DealBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    keyword: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DealAlertBase(BaseModel):
    email: str
    keyword: str

class DealAlertCreate(DealAlertBase):
    pass

class DealAlert(DealAlertBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
