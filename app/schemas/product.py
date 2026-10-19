from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    stock: float
    price_per_kg: float

class ProductResponse(BaseModel):
    id: int
    name: str
    stock: float
    price_per_kg: float

model_config = {
    "from_attributes": True
}