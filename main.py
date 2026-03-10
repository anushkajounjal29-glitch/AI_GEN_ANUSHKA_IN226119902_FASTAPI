
from fastapi import FastAPI

app = FastAPI()

products = [
    {"id": 1, "name": "Smartphone", "price": 15000, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Headphones", "price": 2000, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "Running Shoes", "price": 3000, "category": "Footwear", "in_stock": True},
    {"id": 4, "name": "Backpack", "price": 1200, "category": "Accessories", "in_stock": True},
    {"id": 5, "name": "Laptop Stand", "price": 1500, "category": "Accessories", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 4500, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 2500, "category": "Electronics", "in_stock": True}
]

# Q1 - Show all products
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }


# Q2 - Category Filter
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):

    filtered = [p for p in products if p["category"].lower() == category_name.lower()]

    if not filtered:
        return {"error": "No products found in this category"}

    return {"products": filtered}


# Q3 - Only In-Stock Products
@app.get("/products/instock")
def get_instock_products():

    instock = [p for p in products if p["in_stock"] == True]

    return {
        "in_stock_products": instock,
        "count": len(instock)
    }


# Q4 - Store Summary
@app.get("/store/summary")
def store_summary():

    total = len(products)
    instock = len([p for p in products if p["in_stock"]])
    outstock = total - instock

    categories = list(set(p["category"] for p in products))

    return {
        "store_name": "My E-commerce Store",
        "total_products": total,
        "in_stock": instock,
        "out_of_stock": outstock,
        "categories": categories
    }


# Q5 - Search Products
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    matches = [p for p in products if keyword.lower() in p["name"].lower()]

    if not matches:
        return {"message": "No products matched your search"}

    return {
        "matched_products": matches,
        "total_matches": len(matches)
    }


# BONUS - Best Deal & Premium Pick
@app.get("/products/deals")
def product_deals():

    cheapest = min(products, key=lambda x: x["price"])
    expensive = max(products, key=lambda x: x["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }