from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from app.schemas.order import OrderCreate
from app.services.order_service import create_order_workflow


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

@router.post("/")
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    return create_order_workflow(
        db=db,
        customer_name=order.customer_name,
        product_id=order.product_id,
        quantity=order.quantity,
        amount_paid=order.amount_paid
    )