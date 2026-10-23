from sqlalchemy.orm import Session

from app.models.product import Product

def get_product(
db: Session,
product_id: int
):
    return db.query(Product).filter(
    Product.id == product_id
).first()

def has_sufficient_stock(
product: Product,
quantity: float
) -> bool:
    
  return quantity <= product.stock


def reduce_stock(
product: Product,
quantity: float
):
   if quantity <= 0:
    raise ValueError(
        "Quantity must be greater than zero."
    )
   if quantity > product.stock:
    raise ValueError(
        "Insufficient stock."
    )
   product.stock -= quantity







