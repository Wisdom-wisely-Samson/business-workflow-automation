from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.database import Base

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