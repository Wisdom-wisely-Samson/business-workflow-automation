from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime, timezone
from app.database import Base

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