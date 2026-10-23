
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import create_product


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.get("/", response_model=list[ProductResponse])
def get_products(
    db: Session = Depends(get_db)
):
    products = db.query(Product).all()

    return products


@router.post("/", response_model=ProductResponse)
def register_product(
    product: ProductCreate,
    db: Session = Depends(get_db)   
):
  return create_product(db, product)