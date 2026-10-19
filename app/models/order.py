from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime, timezone
from app.database import Base

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