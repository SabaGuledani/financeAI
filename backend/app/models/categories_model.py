from sqlalchemy import Column, String, Integer
from app.database.db import Base


class Categories(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)


    merchant = Column(String)
    category = Column(String)
    confidence = Column(String)


