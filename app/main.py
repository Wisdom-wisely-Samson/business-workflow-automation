from fastapi import FastAPI, Depends


from .database import Base, engine
from .routers import products, orders, payments, inventory
from .config import APP_NAME

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    version="1.1.0"
    )
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(inventory.router)
@app.get("/")
def home():
    return {
        "message": "Business Workflow Automation API is running"
    }