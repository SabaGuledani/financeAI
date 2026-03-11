from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TransactionBase(BaseModel):
    date: datetime
    details: str
    gel: Optional[float] = None
    usd: Optional[float] = None
    eur: Optional[float] = None
    gbp: Optional[float] = None
    transaction_type: str


class TransactionCreate(TransactionBase):
    """
    Schema for creating a new transaction.
    """

    pass


class TransactionUpdate(BaseModel):
    """
    Schema for partially updating an existing transaction.
    All fields are optional so you can send only what changes.
    """

    date: Optional[datetime] = None
    details: Optional[str] = None
    gel: Optional[float] = None
    usd: Optional[float] = None
    eur: Optional[float] = None
    gbp: Optional[float] = None
    transaction_type: Optional[str] = None


class Transaction(TransactionBase):
    """
    Schema for reading a transaction from the API.
    Includes the database-generated id.
    """

    id: int

    class Config:
        orm_mode = True
