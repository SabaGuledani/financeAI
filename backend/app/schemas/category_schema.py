from pydantic import BaseModel


class CategoryRecord(BaseModel):
    merchant: str
    category: str
    confidence: str
