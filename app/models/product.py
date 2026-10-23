from sqlalchemy import Column, Integer, Float, String
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index = True, autoincrement = True)
    name = Column(String, nullable= False)
    stock = Column(Float, default = 0)
    price_per_kg = Column(Float, nullable = False)