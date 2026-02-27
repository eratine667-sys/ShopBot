import json
import os

DB_FILE = "shop_db.json"

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "products": [],
                "next_id": 1,
                "users": []
            }, f, ensure_ascii=False, indent=2)

def load_db():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_product(category, name, description, price):
    db = load_db()
    product = {
        "id": db["next_id"],
        "category": category,
        "name": name,
        "description": description,
        "price": price
    }
    db["products"].append(product)
    db["next_id"] += 1
    save_db(db)
    return product["id"]

def get_products_by_category(category):
    db = load_db()
    return [p for p in db["products"] if p["category"] == category]

def get_product(product_id):
    db = load_db()
    for p in db["products"]:
        if p["id"] == product_id:
            return p
    return None

def delete_product(product_id):
    db = load_db()
    db["products"] = [p for p in db["products"] if p["id"] != product_id]
    save_db(db)

def add_user(user_id, username):
    db = load_db()
    if user_id not in db["users"]:
        db["users"].append({"id": user_id, "username": username})
        save_db(db)
