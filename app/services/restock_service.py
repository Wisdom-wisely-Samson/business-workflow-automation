from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.sale import Sale

from .audit_service import record_audit
from .inventory_service import get_product, reduce_stock


def resume_waiting_orders(
    db: Session,
    product_id: int
):
    """
    Resume fully paid orders after stock is replenished.

    Orders are processed in FIFO order:
    First In, First Out.
    """

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

    product = get_product(
        db=db,
        product_id=product_id
    )

    if not product:
        return processed_orders

    try:
        for order in waiting_orders:

            # Preserve FIFO: do not skip the oldest eligible order.
            if order.quantity > product.stock:
                break

            # Deduct stock for this order.
            reduce_stock(
                product=product,
                quantity=order.quantity
            )

            # Create a sale record.
            sale = Sale(
                order_id=order.id,
                product_id=product.id,
                quantity=order.quantity,
                amount=order.total_amount,
                status="COMPLETED"
            )

            db.add(sale)

            # Mark the order as completed.
            order.status = "COMPLETED"

            # Record the business event.
            record_audit(
                db=db,
                order_id=order.id,
                action="ORDER_RESUMED_AFTER_RESTOCK",
                description=(
                    "Order resumed after restock. "
                    f"{order.quantity}kg deducted from inventory."
                )
            )

            processed_orders.append(order.id)

        db.commit()

    except Exception:
        db.rollback()
        raise

    return processed_orders

