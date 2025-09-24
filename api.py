"""FastAPI backend for the sales quoting application."""

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import io
import sqlite3
from database import (
    init_database, ProductDB, AccessoryDB, CompatibilityDB, QuoteDB
)

# Initialize FastAPI app
app = FastAPI(title="Sales Quoting API", version="1.0.0")

# Pydantic models for request/response
class ProductModel(BaseModel):
    sku: str
    name: str
    price: float
    description: Optional[str] = ""
    category: Optional[str] = ""
    base_product: Optional[bool] = False

class AccessoryModel(BaseModel):
    sku: str
    name: str
    price: float
    description: Optional[str] = ""

class CompatibilityRule(BaseModel):
    base_product_sku: str
    accessory_sku: str

class QuoteItemModel(BaseModel):
    sku: str
    quantity: int
    item_type: Optional[str] = 'product'

class QuoteModel(BaseModel):
    quote_number: str
    customer_name: Optional[str] = ""
    items: Optional[List[QuoteItemModel]] = []

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Sales Quoting API", "version": "1.0.0"}

# Product endpoints
@app.get("/products", response_model=List[Dict[str, Any]])
async def get_products():
    """Get all products."""
    return ProductDB.get_all_products()

@app.post("/products", status_code=201)
async def create_product(product: ProductModel):
    """Create a new product."""
    try:
        product_id = ProductDB.create_product(
            sku=product.sku,
            name=product.name,
            price=product.price,
            description=product.description,
            category=product.category,
            base_product=product.base_product
        )
        return {"id": product_id, "message": "Product created successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Product with this SKU already exists")

@app.get("/products/{sku}")
async def get_product(sku: str):
    """Get product by SKU."""
    product = ProductDB.get_product_by_sku(sku)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{sku}")
async def update_product(sku: str, product: ProductModel):
    """Update product by SKU."""
    success = ProductDB.update_product(
        sku=sku,
        name=product.name,
        price=product.price,
        description=product.description,
        category=product.category,
        base_product=product.base_product
    )
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated successfully"}

@app.delete("/products/{sku}")
async def delete_product(sku: str):
    """Delete product by SKU."""
    success = ProductDB.delete_product(sku)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# Accessory endpoints
@app.get("/accessories", response_model=List[Dict[str, Any]])
async def get_accessories():
    """Get all accessories."""
    return AccessoryDB.get_all_accessories()

@app.post("/accessories", status_code=201)
async def create_accessory(accessory: AccessoryModel):
    """Create a new accessory."""
    try:
        accessory_id = AccessoryDB.create_accessory(
            sku=accessory.sku,
            name=accessory.name,
            price=accessory.price,
            description=accessory.description
        )
        return {"id": accessory_id, "message": "Accessory created successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Accessory with this SKU already exists")

@app.get("/products/{base_sku}/compatible-accessories")
async def get_compatible_accessories(base_sku: str):
    """Get accessories compatible with a base product."""
    # Verify base product exists
    if not ProductDB.get_product_by_sku(base_sku):
        raise HTTPException(status_code=404, detail="Base product not found")
    
    return AccessoryDB.get_compatible_accessories(base_sku)

# Compatibility rule endpoints
@app.post("/compatibility-rules")
async def add_compatibility_rule(rule: CompatibilityRule):
    """Add a product-accessory compatibility rule."""
    # Verify both products exist
    if not ProductDB.get_product_by_sku(rule.base_product_sku):
        raise HTTPException(status_code=404, detail="Base product not found")
    
    # Check if accessory exists in either products or accessories table
    accessory = ProductDB.get_product_by_sku(rule.accessory_sku)
    if not accessory:
        # Try accessories table
        accessories = AccessoryDB.get_all_accessories()
        if not any(acc['sku'] == rule.accessory_sku for acc in accessories):
            raise HTTPException(status_code=404, detail="Accessory not found")
    
    success = CompatibilityDB.add_compatibility_rule(
        rule.base_product_sku, rule.accessory_sku
    )
    if not success:
        raise HTTPException(status_code=400, detail="Compatibility rule already exists")
    
    return {"message": "Compatibility rule added successfully"}

@app.delete("/compatibility-rules")
async def remove_compatibility_rule(rule: CompatibilityRule):
    """Remove a product-accessory compatibility rule."""
    success = CompatibilityDB.remove_compatibility_rule(
        rule.base_product_sku, rule.accessory_sku
    )
    if not success:
        raise HTTPException(status_code=404, detail="Compatibility rule not found")
    
    return {"message": "Compatibility rule removed successfully"}

@app.get("/compatibility-check/{base_sku}/{accessory_sku}")
async def check_compatibility(base_sku: str, accessory_sku: str):
    """Check if accessory is compatible with base product."""
    is_compatible = CompatibilityDB.is_compatible(base_sku, accessory_sku)
    return {"compatible": is_compatible}

# Quote endpoints
@app.post("/quotes", status_code=201)
async def create_quote(quote: QuoteModel):
    """Create a new quote."""
    try:
        quote_id = QuoteDB.create_quote(quote.quote_number, quote.customer_name)
        
        # Add items to quote if provided
        for item in quote.items:
            # Get price from product or accessory
            product = ProductDB.get_product_by_sku(item.sku)
            unit_price = product['price'] if product else 0
            
            if unit_price == 0:
                # Try accessories table
                accessories = AccessoryDB.get_all_accessories()
                accessory = next((acc for acc in accessories if acc['sku'] == item.sku), None)
                if accessory:
                    unit_price = accessory['price']
            
            if unit_price == 0:
                raise HTTPException(status_code=404, detail=f"SKU {item.sku} not found")
            
            QuoteDB.add_quote_item(quote_id, item.sku, item.quantity, unit_price, item.item_type)
        
        return {"id": quote_id, "message": "Quote created successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Quote with this number already exists")

@app.get("/quotes/{quote_id}")
async def get_quote(quote_id: int):
    """Get quote with all items."""
    quote = QuoteDB.get_quote_with_items(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote

@app.post("/quotes/{quote_id}/items")
async def add_quote_item(quote_id: int, item: QuoteItemModel):
    """Add item to existing quote."""
    # Verify quote exists
    quote = QuoteDB.get_quote_with_items(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Get price
    product = ProductDB.get_product_by_sku(item.sku)
    unit_price = product['price'] if product else 0
    
    if unit_price == 0:
        accessories = AccessoryDB.get_all_accessories()
        accessory = next((acc for acc in accessories if acc['sku'] == item.sku), None)
        if accessory:
            unit_price = accessory['price']
    
    if unit_price == 0:
        raise HTTPException(status_code=404, detail=f"SKU {item.sku} not found")
    
    # Validate compatibility if it's an accessory being added to a quote with base products
    if item.item_type == 'accessory':
        # Get base products in the quote
        base_products = [qi for qi in quote['items'] if qi['item_type'] == 'product']
        if base_products:
            # Check if accessory is compatible with at least one base product
            compatible = False
            for base_product in base_products:
                if CompatibilityDB.is_compatible(base_product['sku'], item.sku):
                    compatible = True
                    break
            
            if not compatible:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Accessory {item.sku} is not compatible with any base products in this quote"
                )
    
    item_id = QuoteDB.add_quote_item(quote_id, item.sku, item.quantity, unit_price, item.item_type)
    return {"id": item_id, "message": "Item added to quote successfully"}

# Bulk upload endpoint
@app.post("/bulk-upload/products")
async def bulk_upload_products(file: UploadFile = File(...)):
    """Bulk upload products from CSV/Excel file."""
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be CSV or Excel format")
    
    try:
        contents = await file.read()
        
        # Read file based on extension
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # Validate required columns
        required_columns = ['sku', 'name', 'price']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_columns}"
            )
        
        successful_imports = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                ProductDB.create_product(
                    sku=str(row['sku']),
                    name=str(row['name']),
                    price=float(row['price']),
                    description=str(row.get('description', '')),
                    category=str(row.get('category', '')),
                    base_product=bool(row.get('base_product', False))
                )
                successful_imports += 1
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        return {
            "message": f"Bulk upload completed",
            "successful_imports": successful_imports,
            "total_rows": len(df),
            "errors": errors
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)