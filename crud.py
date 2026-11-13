from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="FastAPI CRUD Example")

# In-memory database simulation
fake_db = {}

# Pydantic Models for Data Validation
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tax: Optional[float] = None


# 1. CREATE (POST)
@app.post("/items/{item_id}", response_model=Item)
def create_item(item_id: int, item: Item):
    if item_id in fake_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    fake_db[item_id] = item.dict()
    return item


# 2. READ (GET - All items)
@app.get("/items/", response_model=dict)
def read_items():
    return fake_db


# 2. READ (GET - Single item by ID)
@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_db[item_id]


# 3. UPDATE (PUT - Full or partial update using ItemUpdate)
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item_update: ItemUpdate):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    stored_item_data = fake_db[item_id]
    update_data = item_update.dict(exclude_unset=True)
    
    updated_item = {**stored_item_data, **update_data}
    fake_db[item_id] = updated_item
    return updated_item


# 4. DELETE (DELETE)
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del fake_db[item_id]
    return {"message": "Item deleted successfully"}