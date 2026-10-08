from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product
from app.workflow import resume_waiting_orders

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"]
)

@router.post("{product_id}/reduce")
def reduce_stock(
    product_id: int,
    quantity: float,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {
            "success": False,
            "message": "Product not Found"
        }

    if quantity < 0:
        return{
            "success": False, 
            "message": "Quantity must be greater than zero(0)."
        }

    if quantity > product.stock:
        return{
            "success": False,
            "message": "Insufficient stock"
        }

    product.stock -= quantity
    db.commit()
    db.refresh(product)

    return {
        "success": True,
        "message": "Stock reduced.",
        "product_id": product.id,
        "remaining_stock": product.stock
    }


@router.post("/{product}/restock")
def restock_product(
    product_id: int,
    quantity: float,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id== product_id).first()

    if not product:
        return{
            "success": False,
            "message": "Product not found"
        }
    if quantity < 0:
        return{
            "success": False,
            "message": "Quantity must be greater than zero(0)."
        }
    product.stock += quantity

    db.commit()
    db.refresh(product)

    processed_orders = resume_waiting_orders(
        db=db,
        product_id=product_id
    )
    db.refresh(product)

    return{
        "success": True,
        "message": "Inventory has been restocked successfully",
        "product_id": product.id,
        "current_stock": product.stock,
        "orders_completed": processed_orders
    }