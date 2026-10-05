from pydantic import BaseModel


class OrderCreate(BaseModel):
    customer_name: str
    product_id: int
    quantity: float
    amount_paid: float

class PaymentConfirmation(BaseModel):
    amount_paid: float