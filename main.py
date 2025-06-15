from fastapi import FastAPI, HTTPException, Depends
from database import get_db
from sqlalchemy.orm import Session
import models as m
from typing import List
import pyd
from routers import *

app = FastAPI()


app.include_router(user_router, prefix="/api", tags=["api"])
app.include_router(product_router, prefix="/api", tags=["api"])
app.include_router(auth_router)
app.include_router(orders_router, prefix="/api", tags=["api"])