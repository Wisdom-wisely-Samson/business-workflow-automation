from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.sale import Sale
from .audit_service import record_audit
from .inventory_service import get_product, reduce_stock

def confirm_payment_workflow(
db: Session,
order_id: int,
amount_paid: float
):
    

# 1. Find the order.
    order = db.query(Order).filter(
    Order.id == order_id
).first()
    if not order:
         return {
        "success": False,
        "message": "Order not found."
        }
    # 2. Check the order status.
    if order.status != "PENDING_PAYMENT":
        return {
                "success": False,
                "message": (
                    "Order cannot receive payment confirmation. "
                    f"Current status: {order.status}"
                )
            }
    # 3. Validate the payment amount.
    if amount_paid < order.total_amount:
        return {
                "success": False,
                "message": "Payment amount is insufficient.",
                "required": order.total_amount,
                "received": amount_paid,
                "balance": order.total_amount - amount_paid
            }

    Order.amount_paid = amount_paid
    
    # 4. Find the product.
    product = get_product(
    db=db,
    product_id=order.product_id
)
    if not product:
        return {
                "success": False,
                "message": "Product no longer exists."
            }
       # 5. Recheck stock because it may have changed
       # while the order was waiting for payment.
    if not (
    product.stock >= order.quantity
):
        order.status = "WAITING_FOR_STOCK"

        record_audit(
                db=db,
                order_id=order.id,
                action="PAYMENT_CONFIRMED_STOCK_UNAVAILABLE",
                description=(
                    "Payment was confirmed, but stock was insufficient. "
                    f"Required: {order.quantity}kg; "
                    f"available: {product.stock}kg."
                )
            )
        
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
# 6. Update the payment amount.
    order.amount_paid = amount_paid
    # 7. Deduct stock.
    reduce_stock(
    product=product,
    quantity=order.quantity
)
    # 8. Record the sale.
    sale = Sale(
    order_id=order.id,
    product_id=product.id,
    quantity=order.quantity,
    amount=order.total_amount,
    status="COMPLETED"
)
    db.add(sale)
    # 9. Update order status.
    order.status = "COMPLETED"
    # 10. Record the audit event.
    record_audit(
    db=db,
    order_id=order.id,
    action="PAYMENT_CONFIRMED",
    description=(
        f"Payment of {amount_paid} confirmed. "
        f"{order.quantity}kg deducted from inventory."
    )
)
    # 11. Save the changes.
    db.commit()
    return {
    "success": True,
    "status": "COMPLETED",
    "message": "Payment confirmed and order completed.",
    "order_id": order.id
}





