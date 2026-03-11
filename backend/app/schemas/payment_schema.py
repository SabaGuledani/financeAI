from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class PaymentBase(BaseModel):
    date: datetime
    details:str

    gel: Optional[float] = None
    usd: Optional[float] = None
    eur: Optional[float] = None
    gpb: Optional[float] = None
    transaction_object: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    date: Optional[datetime] = None
    details: Optional[str] = None

    gel: Optional[float] = None
    usd: Optional[float] = None
    eur: Optional[float] = None
    gpb: Optional[float] = None
    transaction_object: Optional[str] = None

class Payment(PaymentBase):
    id: int

    class Config:
        orm_mode = True