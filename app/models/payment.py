from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime, timezone
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"

    customer_name = Column(String, nullable=False)
    amount_paid = amount_paid = Column(Float, default=0)
    status = Column(String, default="PENDING_TRANSACTION")

    created_at = Column(
            DateTime,
            default=datetime.now(timezone.utc)
        )