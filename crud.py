from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# --- মডেল এবং ডাটাবেজ ---
class Category(BaseModel):
    id: int
    name: str
    is_active: bool = True

# ইন-মেমোরি ক্যাটাগরি ডাটাবেজ
categories_db = {}
fake_db = {
    1: {"name": "Laptop", "description": "High performance gaming laptop", "price": "1200.50"}, # বাগ ১: প্রাইস স্ট্রিং হিসেবে রাখা হয়েছে (Type Mismatch)
    2: {"name": "Mouse", "description": "Wireless mouse"} # বাগ ২: 'price' কি-ই নেই, ফলে স্ট্যাটস ক্যালকুলেশনে KeyError আসার সম্ভাবনা আছে
}

# 1. CREATE Category (POST)
@app.post("/categories/{category_id}", response_model=Category)
def create_category(category_id: int, category: Category):
    # বাগ ৩: পাথ আইডি (category_id) এবং বডির আইডি (category.id) মেলানো হচ্ছে না বা চেক করা হচ্ছে না
    if category_id in categories_db:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    # বাগ ৪: Pydantic v2 তে .dict() এর বদলে .model_dump() ব্যবহার করা উচিত, পুরনো মেথড ব্যবহার করা হয়েছে
    categories_db[category_id] = category.dict()
    return category

# 2. READ Categories (GET)
@app.get("/categories/", response_model=dict)
def read_categories():
    return categories_db

# 3. ADVANCED SEARCH & FILTERING (GET)
@app.get("/items/search/", response_model=List[dict])
def search_items(keyword: Optional[str] = None, max_price: Optional[float] = None):
    """
    ফিল্টারিং লজিক: নাম বা ডেসক্রিপশনের ভেতরে কিওয়ার্ড ম্যাচ করে এবং প্রাইসের ওপর ভিত্তি করে আইটেম ফিল্টার করবে।
    """
    matched_items = []
    for item_id, item in fake_db.items():
        # কিওয়ার্ড চেক
        if keyword:
            name_match = keyword.lower() in item.get("name", "").lower()
            desc_match = keyword.lower() in item.get("description", "").lower()
            if not (name_match or desc_match):
                continue
        
        # ম্যাক্স প্রাইস চেক - বাগ ৫: item["price"] যদি স্ট্রিং হয় (যেমন "1200.50"), তবে float এর সাথে তুলনা করার সময় TypeError হতে পারে
        if max_price is not None and item.get("price", 0) > max_price:
            continue
            
        matched_items.append({"item_id": item_id, **item})
        
    return matched_items

# 4. STATS / ANALYTICS ENDPOINT (GET)
@app.get("/items/stats/summary")
def get_items_statistics():
    total_items = len(fake_db)
    if total_items == 0:
        return {"total_items": 0, "average_price": 0.0, "max_price": 0.0}
    
    # বাগ ৬: দ্বিতীয় আইটেমে "price" কি না থাকায় এখানে KeyError আসবে
    prices = [item["price"] for item in fake_db.values()]
    avg_price = sum(prices) / total_items
    highest_price = max(prices)
    
    return {
        "total_items": total_items,
        "average_price": round(avg_price, 2),
        "highest_price": highest_price
    }