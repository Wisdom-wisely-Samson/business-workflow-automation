from pydantic import BaseModel

class PaymentConfirmation(BaseModel):
    amount_paid: float