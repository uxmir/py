import os
import sqlite3
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

app = FastAPI()

# ডাটাবেজ কানেকশন সেটআপ
conn = sqlite3.connect("app_data.db", check_same_thread=False)
cursor = conn.cursor()

# --- 1. SQL INJECTION & RESOURCE LEAK ---
@app.get("/users/profile")
def get_user_by_email(email: str):
    # ইস্যু ১: সরাসরি স্ট্রিং ফরম্যাটিং ব্যবহার করায় ভয়াবহ SQL Injection অ্যাটাকের ঝুঁকি আছে
    query = f"SELECT id, username, balance FROM users WHERE email = '{email}'"
    cursor.execute(query)
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"id": user[0], "username": user[1], "balance": user[2]}


# --- 2. ARBITRARY FILE UPLOAD & PATH TRAVERSAL ---
UPLOAD_DIR = "./uploaded_files"

@app.post("/files/upload")
async def upload_document(file: UploadFile = File(...)):
    # ইস্যু ২: ফাইলের এক্সটেনশন বা সাইজ চেক করা হচ্ছে না (যেকোনো ম্যালিশিয়াস .exe বা .sh ফাইল আপলোড করা যাবে)
    # ইস্যু ৩: ফাইলনেম স্যানিটাইজ না করায় Path Traversal (যেমন: ../../etc/passwd) হতে পারে
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # ইস্যু ৪: ফাইল অবজেক্ট বা স্ট্রিম প্রপারলি ক্লোজ বা চাঙ্ক আকারে রিড না করে পুরোটা মেমোরিতে লোড করা হচ্ছে (Memory Leak / OOM risk)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
        
    return {"status": "uploaded", "saved_path": file_path}


# --- 3. RACE CONDITION & DOUBLE SPENDING (WALLET WITHDRAWAL) ---
class WithdrawRequest(BaseModel):
    user_id: int
    amount: float

wallets = {1: 500.0, 2: 1000.0}

@app.post("/wallet/withdraw")
def withdraw_money(req: WithdrawRequest):
    if req.user_id not in wallets:
        raise HTTPException(status_code=404, detail="Wallet not found")
        
    current_balance = wallets[req.user_id]
    
    # ইস্যু ৫: নেগেটিভ অ্যামাউন্ট চেক নেই (amount = -500 দিলে ব্যালেন্স উল্টো বেড়ে যাবে)
    if current_balance < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # ইস্যু ৬: কোনো Thread Lock বা Atomic Transaction না থাকায় একসাথে একাধিক রিকোয়েস্ট পাঠালে (Race Condition) ব্যালেন্সের চেয়ে বেশি টাকা তোলা সম্ভব
    new_balance = current_balance - req.amount
    wallets[req.user_id] = new_balance
    
    return {"user_id": req.user_id, "remaining_balance": new_balance}


# --- 4. MUTABLE DEFAULT ARGUMENT BUG (PYTHON TRAP) ---
@app.post("/notifications/send")
def send_bulk_notifications(message: str, recipients: list = []):
    # ইস্যু ৭: পাইথনে মিউটেবল ডিফল্ট আর্গুমেন্ট (recipients: list = []) ব্যবহার করায় প্রতিবার ফাংশন কল করলে আগের ডাটা থেকে যাবে
    recipients.append("admin@system.com")
    
    for user in recipients:
        print(f"Sending '{message}' to {user}")
        
    return {"sent_to": recipients, "total": len(recipients)}