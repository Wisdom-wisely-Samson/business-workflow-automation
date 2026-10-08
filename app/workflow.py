from sqlalchemy.orm import Session

from .models import Order, Product, Sale, AuditLog


def create_order_workflow(
    db: Session,
    customer_name: str,
    product_id: int,
    quantity: float,
    amount_paid: float
):

    # 1. Find product
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        return {
            "success": False,
            "message": "Product not found."
        }

    # 2. Validate quantity
    if quantity <= 0:
        return {
            "success": False,
            "message": "Quantity must be greater than zero."
        }

    # 3. Calculate total
    total_amount = quantity * product.price_per_kg

    # 4. Check stock FIRST
    if quantity > product.stock:

        order = Order(
            customer_name=customer_name,
            product_id=product_id,
            quantity=quantity,
            total_amount=total_amount,
            amount_paid=amount_paid,
            status="WAITING_FOR_STOCK"
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        audit = AuditLog(
            order_id=order.id,
            action="WAITING_FOR_STOCK",
            description=(
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

    # 5. Create order
    order = Order(
        customer_name=customer_name,
        product_id=product_id,
        quantity=quantity,
        total_amount=total_amount,
        amount_paid=amount_paid
    )

    db.add(order)
    db.flush()

    # 6. Check payment
    if amount_paid < total_amount:

        order.status = "PENDING_PAYMENT"

        audit = AuditLog(
            order_id=order.id,
            action="PENDING_PAYMENT",
            description=(
                f"Payment pending. Required: "
                f"{total_amount}, received: {amount_paid}."
            )
        )

        db.add(audit)
        db.commit()

        return {
            "success": False,
            "status": "PENDING_PAYMENT",
            "message": (
                "Payment is required before processing "
                "the order."
            ),
            "amount_required": total_amount,
            "amount_paid": amount_paid,
            "balance": total_amount - amount_paid,
            "order_id": order.id
        }

    # 7. Payment confirmed
    order.status = "PROCESSING"

    # 8. Reduce stock
    product.stock -= quantity

    # 9. Record sale
    sale = Sale(
        order_id=order.id,
        product_id=product.id,
        quantity=quantity,
        amount=total_amount,
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

    # 11. Complete order
    order.status = "COMPLETED"

    # 12. Save everything
    db.commit()

    return {
        "success": True,
        "status": "COMPLETED",
        "message": "Order processed successfully.",
        "order_id": order.id
    }
def resume_waiting_orders(
        product_id: int,
        db: Session
):
    waiting_orders = db.query(Order).filter(Order.product_id == product_id, Order.status== "WAITING_FOR_STOCK").all()
    processed_orders = []

    for order in waiting_orders:

        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            continue

        if order.quantity > product.stock:
            continue

        product.stock -= order.quantity

        sale = Sale(
            order_id=order.id,
            product_id=product.id,
            quantity=order.quantity,
            amount=order.total_amount,
            status="COMPLETED"

        )
        db.add(sale)

        order.status = "COMPLETED"

        audit= AuditLog(
            order_id=order.id,
            action= "ORDER RESUMED AFTER RESTOCK",
            description=(
                f"Order resumed after restock. "
                f"{order.quantity}kg removed from inventory."
            )
        )

        db.add(audit)

        processed_orders.append(order.id)
        db.commit()
        return processed_orders


