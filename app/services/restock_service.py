from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.sale import Sale
from .audit_service import record_audit
from .inventory_service import get_product, reduce_stock

def resume_waiting_orders(
db: Session,
product_id: int
):
    
    waiting_orders = (
    db.query(Order)
    .filter(
        Order.product_id == product_id,
        Order.status == "WAITING_FOR_STOCK",
        Order.amount_paid >= Order.total_amount
    )
    .order_by(
        Order.created_at.asc(),
        Order.id.asc()
    )
    .all()
)
    

    processed_orders = []
    for order in waiting_orders:
        product = get_product(
                db=db,
                product_id=product_id
            )
        
        
        if not product:
                break
        
            # Stop if the oldest remaining order cannot be fulfilled.
            # This preserves FIFO priority.
        if order.quantity > product.stock:
                break


    

    # 4. Deduct stock.
    reduce_stock(
        product=product,
        quantity=order.quantity
    )

    # 5. Record the sale.
    sale = Sale(
        order_id=order.id,
        product_id=product.id,
        quantity=order.quantity,
        amount=order.total_amount,
        status="COMPLETED"
    )


    db.add(sale)

    # 6. Update the order status.
    order.status = "COMPLETED"

    # 7. Record the event.
    record_audit(
        db=db,
        order_id=order.id,
        action="ORDER_RESUMED_AFTER_RESTOCK",
        description=(
            f"Order resumed after restock. "
            f"{order.quantity}kg deducted from inventory."
        )
    )

    processed_orders.append(order.id)

    db.commit()

    return processed_orders

