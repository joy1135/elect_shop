from fastapi import FastAPI
from routers import *

app = FastAPI()

app.include_router(user_router, prefix="/api", tags=["api"])
app.include_router(product_router, prefix="/api", tags=["api"])
app.include_router(auth_router)
app.include_router(orders_router, prefix="/api", tags=["api"])
app.include_router(review_router, prefix="/api", tags=["api"])
app.include_router(category_router, prefix="/api", tags=["api"])