from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.sale import Sale
from .audit_service import record_audit
from .inventory_service import get_product, reduce_stock


def create_order_workflow(
    db: Session,
    customer_name: str,
    product_id: int,
    quantity: float,
    amount_paid: float
):
    """
    Handles the full order workflow:
    - Validates input
    - Creates order
    - Checks stock and payment
    - Records audit logs
    - Deducts stock and records sale
    """

    # 1. Validate customer name
    if not customer_name.strip():
        return {"success": False, "message": "Customer name is required."}

    # 2. Validate quantity
    if quantity <= 0:
        return {"success": False, "message": "Quantity must be greater than zero."}

    # 3. Validate payment amount
    if amount_paid < 0:
        return {"success": False, "message": "Payment amount cannot be negative."}

    # 4. Find the product
    product = get_product(db=db, product_id=product_id)
    if not product:
        return {"success": False, "message": "Product not found."}

    # 5. Calculate total order amount
    total_amount = quantity * product.price_per_kg

    # 6. Check stock before processing payment
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
        db.flush()

        record_audit(
            db=db,
            order_id=order.id,
            action="WAITING_FOR_STOCK",
            description=f"Requested {quantity}kg, but only {product.stock}kg is available."
        )
        db.commit()

        return {
            "success": False,
            "status": "WAITING_FOR_STOCK",
            "message": "Insufficient stock. Customer and manager should be notified.",
            "order_id": order.id
        }

    # 7. Create the order
    order = Order(
        customer_name=customer_name,
        product_id=product_id,
        quantity=quantity,
        total_amount=total_amount,
        amount_paid=amount_paid
    )
    db.add(order)
    db.flush()

    # 8. Check whether the full payment has been received
    if amount_paid < total_amount:
        order.status = "PENDING_PAYMENT"

        record_audit(
            db=db,
            order_id=order.id,
            action="PENDING_PAYMENT",
            description=f"Payment pending. Required: {total_amount}; received: {amount_paid}."
        )
        db.commit()

        return {
            "success": False,
            "status": "PENDING_PAYMENT",
            "message": "Payment is required before processing the order.",
            "amount_required": total_amount,
            "amount_paid": amount_paid,
            "balance": total_amount - amount_paid,
            "order_id": order.id
        }

    # 9. Full payment reported — recheck stock before reducing it
    if quantity > product.stock:
        order.status = "WAITING_FOR_STOCK"

        record_audit(
            db=db,
            order_id=order.id,
            action="PAYMENT_CONFIRMED_STOCK_UNAVAILABLE",
            description="Payment was reported, but stock became insufficient before order completion."
        )
        db.commit()

        return {
            "success": False,
            "status": "WAITING_FOR_STOCK",
            "message": "Payment was reported, but stock is insufficient to fulfill the order.",
            "order_id": order.id
        }

    # 10. Deduct stock
    reduce_stock(product=product, quantity=quantity)

    # 11. Record the sale
    sale = Sale(
        order_id=order.id,
        product_id=product.id,
        quantity=quantity,
        amount=total_amount,
        status="COMPLETED"
    )
    db.add(sale)

    # 12. Complete the order
    order.status = "COMPLETED"
    record_audit(
        db=db,
        order_id=order.id,
        action="ORDER_COMPLETED",
        description=f"Order completed. {quantity}kg deducted from inventory."
    )
    db.commit()

    return {
        "success": True,
        "status": "COMPLETED",
        "message": "Order processed successfully.",
        "order_id": order.id
    }
