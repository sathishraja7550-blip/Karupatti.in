from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Karupatti Village Food Backend")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Product(BaseModel):
    id: int
    name: str
    price: float
    stock: int

class Order(BaseModel):
    id: int
    product_id: int
    quantity: int
    total_price: Optional[float] = 0.0

products: List[Product] = [
    Product(id=1, name="Karupatti", price=480, stock=10),
    Product(id=2, name="Pure Honey", price=300, stock=15),
    Product(id=3, name="Panam Kalkandu", price=350, stock=20),
]
orders: List[Order] = []

@app.get("/", response_class=HTMLResponse)
def serve_homepage(request: Request):
    return templates.TemplateResponse("sathis-project.html", {"request": request})

@app.get("/api/products", response_model=List[Product])
def get_products():
    return products

@app.post("/api/products", response_model=Product)
def add_product(product: Product):
    products.append(product)
    return product

@app.post("/api/orders", response_model=Order)
def create_order(order: Order):
    for p in products:
        if p.id == order.product_id:
            if p.stock < order.quantity:
                raise HTTPException(status_code=400, detail="Not enough stock")
            p.stock -= order.quantity
            order.total_price = p.price * order.quantity
            orders.append(order)
            return order
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/api/orders", response_model=List[Order])
def get_orders():
    return orders
