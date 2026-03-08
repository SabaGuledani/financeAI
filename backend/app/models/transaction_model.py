from sqlalchemy import Column, String, Integer, Float, DateTime
from app.database.db import Base
import datetime

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    date = Column(DateTime)

    details = Column(String)

    gel = Column(Float)
    usd = Column(Float)
    eur = Column(Float)
    gbp = Column(Float)

    transaction_type = Column(String)

