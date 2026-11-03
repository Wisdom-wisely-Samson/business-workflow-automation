from pydantic import BaseModel, ConfigDict, Field

class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    stock: float = Field(ge=0)
    price_per_kg: float = Field(gt=0)

class ProductResponse(BaseModel):
    id: int
    name: str
    stock: float
    price_per_kg: float

    model_config = ConfigDict(from_attributes=True)