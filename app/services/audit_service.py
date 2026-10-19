from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.product import Product
from app.models.sale import Sale
from app.models.audit_log import AuditLog

def record_audit(
db: Session,
order_id: int,
action: str,
description: str
):
    audit = AuditLog(
    order_id=order_id,
    action=action,
    description=description
)
    db.add(audit)
    return audit

