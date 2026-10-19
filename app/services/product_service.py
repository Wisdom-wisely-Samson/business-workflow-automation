from sqlalchemy.orm import Session
from app.models.product import Product
from app.exeptions import ConflictException

def create_product(
        db: Session, product_data
):
    existing_product = db.query(Product).filter(Product.name == product_data.name).first()
    if existing_product:
        raise ConflictException(
            "Product already exist"
        )
    product = Product(
        name=product_data.name,
        stock=product_data.stock,
        price_per_kg=product_data.price_per_kg
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product