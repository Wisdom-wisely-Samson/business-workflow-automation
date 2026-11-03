from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1)
    product_id: int = Field(gt=0)
    quantity: float = Field(gt=0)
    amount_paid: float = Field(ge=0)