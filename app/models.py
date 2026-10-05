from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime, timezone
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index = True)
    name = Column(String, nullable= False)
    stock = Column(Float, default = 0)
    price_per_kg = Column(Float, nullable = False)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    customer_name = Column(String, nullable=False)
    product_id = Column(Integer, nullable=False)

    quantity = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0)

    status = Column(String, default="PENDING_PAYMENT")

    created_at = Column(
        DateTime,
        default=datetime.now(timezone.utc)
    )


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)

    quantity = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)

    status = Column(String, default="COMPLETED")

    created_at = Column(
        DateTime,
        default=datetime.now(timezone.utc)
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    description = Column(String, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.now(timezone.utc)
    )