import hashlib
import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

app = FastAPI()

# --- ডামি ডাটাবেজ ---
users_db = {}
orders_db = []
SECRET_API_KEY = "sk_live_9876543210_super_secret" # ইস্যু ১: হার্ডকোডেড সিক্রেট কী

class UserRegister(BaseModel):
    username: str
    password: str
    email: str

class OrderCreate(BaseModel):
    user_id: int
    items: List[dict]
    coupon_code: Optional[str] = None

# 1. USER REGISTRATION (Security Vulnerability Test)
@app.post("/users/register")
def register_user(user: UserRegister):
    # ইস্যু ২: পাসওয়ার্ড হ্যাশিংয়ের জন্য দুর্বল MD5 অ্যালগরিদম ব্যবহার (Salt ছাড়া)
    hashed_password = hashlib.md5(user.password.encode()).hexdigest()
    
    user_id = len(users_db) + 1
    users_db[user_id] = {
        "username": user.username,
        "password": hashed_password,
        "email": user.email
    }
    # ইস্যু ৩: রেসপন্সে হ্যাশ করা পাসওয়ার্ডও রিটার্ন করে দেওয়া হচ্ছে
    return {"message": "User created", "data": users_db[user_id]}


# 2. ORDER PROCESSING & DISCOUNT (Logic & Edge-case Bugs)
@app.post("/orders/")
def create_order(order: OrderCreate, x_api_key: Optional[str] = Header(None)):
    # ইস্যু ৪: টাইমিং অ্যাটাক (Timing Attack) প্রতিরোধী তুলনা (hmac.compare_digest) ব্যবহার করা হয়নি
    if x_api_key != SECRET_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    if order.user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    total_amount = 0
    for item in order.items:
        # ইস্যু ৫: নেগেটিভ প্রাইস বা কোয়ান্টিটি চেক করা হচ্ছে না (যেমন: qty = -5 দিলে বিল কমে যাবে)
        total_amount += item["price"] * item["qty"]

    # কুপন লজিক
    if order.coupon_code == "SAVE50":
        total_amount = total_amount - 50 # ইস্যু ৬: টোটাল বিল ৫০ টাকার কম হলে নেগেটিভ বিল হয়ে যাবে

    new_order = {
        "order_id": len(orders_db) + 1,
        "user_id": order.user_id,
        "total": total_amount,
        "status": "confirmed"
    }
    orders_db.append(new_order)
    return new_order


# 3. BULK REPORT GENERATOR (Performance & Infinite Loop Risk)
@app.get("/orders/report")
def generate_report(limit: int = 10):
    report = []
    count = 0
    
    # ইস্যু ৭: orders_db খালি থাকলে বা limit এর চেয়ে কম আইটেম থাকলে ইনফিনিট লুপে (Infinite Loop) পড়ে যাবে
    while count < limit:
        if count < len(orders_db):
            report.append(orders_db[count])
            count += 1
        # count বাড়ানোর এলস কন্ডিশন নেই!
        
    # ইস্যু ৮: অপ্রয়োজনীয় স্লিপ যা অ্যাসিঙ্ক বা মেইন থ্রেড ব্লক করবে
    time.sleep(5) 
    return {"total_fetched": len(report), "orders": report}