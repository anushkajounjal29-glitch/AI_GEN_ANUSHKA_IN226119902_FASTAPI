from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Product database
products = {
    1: {"name": "Wireless Mouse", "price": 499, "stock": 10},
    2: {"name": "Notebook", "price": 99, "stock": 50},
    3: {"name": "USB Hub", "price": 299, "stock": 0},
    4: {"name": "Pen Set", "price": 49, "stock": 20}
}

cart = {}
orders = []
order_id_counter = 1


class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str


# Add to cart
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    product = products[product_id]

    if product["stock"] == 0:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    if product_id in cart:
        cart[product_id]["quantity"] += quantity
        message = "Cart updated"
    else:
        cart[product_id] = {
            "product_id": product_id,
            "product_name": product["name"],
            "quantity": quantity,
            "unit_price": product["price"]
        }
        message = "Added to cart"

    cart[product_id]["subtotal"] = cart[product_id]["quantity"] * product["price"]

    return {
        "message": message,
        "cart_item": cart[product_id]
    }


# View cart
@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    items = list(cart.values())
    grand_total = sum(item["subtotal"] for item in items)

    return {
        "items": items,
        "item_count": len(items),
        "grand_total": grand_total
    }


# Remove item
@app.delete("/cart/{product_id}")
def remove_item(product_id: int):

    if product_id not in cart:
        raise HTTPException(status_code=404, detail="Item not in cart")

    removed = cart.pop(product_id)

    return {"message": f"{removed['product_name']} removed from cart"}


# Checkout
@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):

    global order_id_counter

    if not cart:
        raise HTTPException(status_code=400, detail="CART_EMPTY")

    placed_orders = []

    for item in cart.values():

        order = {
            "order_id": order_id_counter,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"],
            "delivery_address": data.delivery_address
        }

        orders.append(order)
        placed_orders.append(order)

        order_id_counter += 1

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": placed_orders,
        "grand_total": sum(o["total_price"] for o in placed_orders)
    }


# View orders
@app.get("/orders")
def get_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }
@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):

    global order_id_counter

    # BONUS CONDITION
    if not cart:
        raise HTTPException(status_code=400, detail="CART_EMPTY")

    placed_orders = []

    for item in cart.values():

        order = {
            "order_id": order_id_counter,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"],
            "delivery_address": data.delivery_address
        }

        orders.append(order)
        placed_orders.append(order)

        order_id_counter += 1

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": placed_orders,
        "grand_total": sum(o["total_price"] for o in placed_orders)
    }