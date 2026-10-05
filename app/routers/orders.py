from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Product


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post("/")
def create_product(
    name: str,
    stock: float,
    price_per_kg: float,
    db: Session = Depends(get_db)   
):
    

    product = Product(
        name=name,
        stock=stock,
        price_per_kg=price_per_kg
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product