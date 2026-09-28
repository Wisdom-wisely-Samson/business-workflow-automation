from sqlalchemy.orm import Session
from .models import Order, Product, Sale, AuditLog

def create_order_workflow(
        db: Session, 
        customer_name: str,
        product_id: int,
        quantity: float,
        amount_paid: float
):

    product = db.query(Product).filter(
        Product.id == product_id).first(
    )
    if not product:
        return{
            "success": False,
            "message": "Product not found."
        }

    if quantity <= 0:
        return{
            "success": False,
            "message": "Quantity must be greater than zero."
        }

    if quantity > product.stock:

        order = Order(
            customer_name=customer_name,
            product_id=product_id,
            quantity=quantity,
            total_amount=quantity * product.price_per_kg,
            amount_paid=amount_paid,
            status="WAITING_FOR_STOCK"
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        audit = AuditLog(
            order_id = order.id,
            action = "WAITING_FOR_STOCK",
            description = (
                 f"Requested {quantity}kg but only "
                f"{product.stock}kg is available."
            )
        )

        db.add(audit)
        db.commit()

        return {
            "success": False,
            "status": "WAITING_FOR_STOCK",
            "message": (
                "Insufficient stock. "
                "Customer and manager should be notified."
            ),
            "order_id": order.id
        }
    order.status = "PROCESSING"

    db.add(order)

    # 8. Reduce stock
    product.stock -= quantity

    # 9. Record sale
    sale = Sale(
        order_id=order.id,
        product_id=product.id,
        quantity=quantity,
        amount=amount_paid,
        status="COMPLETED"
    )

    db.add(sale)

    # 10. Audit
    audit = AuditLog(
        order_id=order.id,
        action="ORDER_COMPLETED",
        description=(
            f"Order processed successfully. "
            f"{quantity}kg removed from inventory."
        )
    )

    db.add(audit)

    # 11. Complete transaction
    order.status = "COMPLETED"

    db.commit()

    return {
        "success": True,
        "status": "COMPLETED",
        "message": "Order processed successfully.",
        "order_id": order.id
    }