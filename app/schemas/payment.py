from pydantic import BaseModel, Field

class PaymentConfirmation(BaseModel):
    amount_paid: float = Field(ge=0)