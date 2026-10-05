from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Order, Product, Sale, AuditLog
from ..schemas import PaymentConfirmation

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

@router.post("/{order_id}/confirm")
def confirm_payment(
    order_id: int,
    payment: PaymentConfirmation,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return{
            "success": False,
            "message": "Order not found"
        }

    if order.status != "PENDING_PAYMENT":
        return {
            "success": False,
            "message": (
                f"Order can not receive payment confirmation."
                f"Current status is {Order.status}"
            )
        }

    if payment.amount_paid < order.total_amount:
        return{
            "success": False,
            "message": "Payment amount is insufficient.",
            "required": order.total_amount,
            "received": payment.amount_paid,
            "balance": (
                order.total_amount - payment.amount_paid
            )
        }

    product = db.query(Product).filter(
        Product.id == order.product_id
    ).first()

    if not product:
        return {
            "success": False,
            "message": "Product no longer exists."
        }

    # 5. RE-CHECK STOCK
    if order.quantity > product.stock:

        order.status = "WAITING_FOR_STOCK"

        audit = AuditLog(
            order_id=order.id,
            action="PAYMENT_CONFIRMED_STOCK_UNAVAILABLE",
            description=(
                f"Payment confirmed, but stock is insufficient. "
                f"Required: {order.quantity}kg, "
                f"available: {product.stock}kg."
            )
        )

        db.add(audit)
        db.commit()

        return {
            "success": False,
            "status": "WAITING_FOR_STOCK",
            "message": (
                "Payment confirmed, but there is not enough "
                "stock to fulfill the order."
            ),
            "order_id": order.id
        }

    # 6. Payment is confirmed
    order.amount_paid = payment.amount_paid
    order.status = "PROCESSING"

    # 7. Reduce stock
    product.stock -= order.quantity

    # 8. Record sale
    sale = Sale(
        order_id=order.id,
        product_id=product.id,
        quantity=order.quantity,
        amount=order.total_amount,
        status="COMPLETED"
    )

    db.add(sale)

    # 9. Create audit log
    audit = AuditLog(
        order_id=order.id,
        action="PAYMENT_CONFIRMED",
        description=(
            f"Payment of {payment.amount_paid} confirmed. "
            f"{order.quantity}kg removed from inventory."
        )
    )

    db.add(audit)

    # 10. Complete order
    order.status = "COMPLETED"

    # 11. Save everything
    db.commit()

    return {
        "success": True,
        "status": "COMPLETED",
        "message": "Payment confirmed and order completed.",
        "order_id": order.id
    }