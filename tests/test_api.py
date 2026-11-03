import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


class OrderPaymentWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        test_session = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

        def override_get_db():
            db = test_session()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_paid_order_waits_for_stock_then_completes_after_restock(self):
        product_response = self.client.post(
            "/products/",
            json={"name": "Coffee", "stock": 2, "price_per_kg": 10},
        )
        self.assertEqual(product_response.status_code, 200)
        product_id = product_response.json()["id"]

        order_response = self.client.post(
            "/orders/",
            json={
                "customer_name": "Alex",
                "product_id": product_id,
                "quantity": 2,
                "amount_paid": 0,
            },
        )
        self.assertEqual(order_response.json()["status"], "PENDING_PAYMENT")
        order_id = order_response.json()["order_id"]

        reduce_response = self.client.post(
            f"/inventory/{product_id}/reduce",
            params={"quantity": 2},
        )
        self.assertEqual(reduce_response.status_code, 200)

        payment_response = self.client.post(
            f"/payments/{order_id}/confirm",
            json={"amount_paid": 20},
        )
        self.assertEqual(payment_response.json()["status"], "WAITING_FOR_STOCK")

        restock_response = self.client.post(
            f"/inventory/{product_id}/restock",
            params={"quantity": 2},
        )
        self.assertEqual(restock_response.status_code, 200)
        self.assertEqual(restock_response.json()["orders_completed"], [order_id])
        self.assertEqual(restock_response.json()["current_stock"], 0)

    def test_inventory_adjustment_requires_positive_quantity(self):
        product_response = self.client.post(
            "/products/",
            json={"name": "Coffee", "stock": 2, "price_per_kg": 10},
        )
        product_id = product_response.json()["id"]

        response = self.client.post(
            f"/inventory/{product_id}/reduce",
            params={"quantity": 0},
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
