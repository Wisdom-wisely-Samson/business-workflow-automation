from fastapi import FastAPI, Depends, Request
from app.exeptions import AppException
from fastapi.responses import JSONResponse


from .database import Base, engine
from .routers import products, orders, payments, inventory
from .config import APP_NAME

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    version="1.1.0"
    )

@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message
        }
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