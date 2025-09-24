# Sales Quoting Application

A comprehensive sales quoting system built with FastAPI, Streamlit, and SQLite.

## Features

- **Product Management**: Add, edit, delete, and view products
- **Accessory Management**: Manage accessories and their compatibility with base products
- **Compatibility Rules**: Define which accessories work with which base products
- **Quote Builder**: Interactive cart system with compatibility validation
- **Bulk Upload**: Import products from CSV/Excel files
- **Real-time Calculations**: Automatic total calculation in quotes

## Architecture

- **Backend**: FastAPI with SQLite database
- **Frontend**: Streamlit web interface
- **Database**: SQLite with tables for products, accessories, compatibility rules, and quotes

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Populate Sample Data** (Optional):
   ```bash
   python sample_data.py
   ```

## Running the Application

### Method 1: Using Startup Scripts

1. **Start the API Server** (Terminal 1):
   ```bash
   python start_api.py
   ```
   The API will be available at: http://localhost:8000

2. **Start the Frontend** (Terminal 2):
   ```bash
   python start_frontend.py
   ```
   The web interface will be available at: http://localhost:8501

### Method 2: Manual Start

1. **Start API Server**:
   ```bash
   uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Streamlit Frontend**:
   ```bash
   streamlit run frontend.py
   ```

## Usage Guide

### 1. Product Management
- Navigate to "Product Management" in the sidebar
- **View Products**: See all products in a table
- **Add Product**: Fill out the form to add new products
- **Edit/Delete**: Select a product to modify or remove

### 2. Accessory Management  
- Navigate to "Accessory Management"
- Add accessories that can be sold with base products
- View all existing accessories

### 3. Compatibility Rules
- Navigate to "Compatibility Rules"
- **Add Rule**: Define which accessories work with which base products
- **View Compatible**: See all accessories compatible with a specific base product

### 4. Quote Builder
- Navigate to "Quote Builder"
- **Add Products**: Select and add base products to cart
- **Add Accessories**: Only compatible accessories will be shown based on products in cart
- **Cart Management**: View total, remove items, clear cart
- **Save Quote**: Create a quote with quote number and customer info

### 5. Bulk Upload
- Navigate to "Bulk Upload"
- Upload CSV or Excel files with product data
- Required columns: `sku`, `name`, `price`
- Optional columns: `description`, `category`, `base_product`

## API Endpoints

The FastAPI backend provides the following endpoints:

### Products
- `GET /products` - Get all products
- `POST /products` - Create new product
- `GET /products/{sku}` - Get product by SKU
- `PUT /products/{sku}` - Update product
- `DELETE /products/{sku}` - Delete product

### Accessories
- `GET /accessories` - Get all accessories
- `POST /accessories` - Create new accessory
- `GET /products/{base_sku}/compatible-accessories` - Get compatible accessories

### Compatibility
- `POST /compatibility-rules` - Add compatibility rule
- `DELETE /compatibility-rules` - Remove compatibility rule
- `GET /compatibility-check/{base_sku}/{accessory_sku}` - Check compatibility

### Quotes
- `POST /quotes` - Create new quote
- `GET /quotes/{quote_id}` - Get quote with items
- `POST /quotes/{quote_id}/items` - Add item to quote

### Bulk Upload
- `POST /bulk-upload/products` - Bulk upload products from file

## Database Schema

### Products Table
- `id` (Primary Key)
- `sku` (Unique)
- `name`
- `description`
- `price`
- `category`
- `base_product` (Boolean)
- `created_at`

### Accessories Table
- `id` (Primary Key)
- `sku` (Unique)
- `name`
- `description`
- `price`
- `created_at`

### Product Accessory Rules Table
- `id` (Primary Key)
- `base_product_sku` (Foreign Key)
- `accessory_sku` (Foreign Key) 
- `created_at`

### Quotes Table
- `id` (Primary Key)
- `quote_number` (Unique)
- `customer_name`
- `total_amount`
- `status`
- `created_at`
- `updated_at`

### Quote Items Table
- `id` (Primary Key)
- `quote_id` (Foreign Key)
- `sku`
- `quantity`
- `unit_price`
- `line_total`
- `item_type`
- `created_at`

## Sample Data

The application includes sample data for HP Plotters:

**Base Products:**
- HP DesignJet T120 24-inch ($999.99)
- HP DesignJet T520 36-inch ($1,499.99)
- HP DesignJet T730 36-inch ($2,299.99)

**Accessories:**
- Stands (model-specific)
- Paper rolls (size-specific)
- Ink cartridges (compatible with all models)

## Validation Rules

The system enforces these business rules:

1. **Accessory Compatibility**: Accessories can only be added to quotes if they are compatible with at least one base product in the quote
2. **SKU Uniqueness**: All product and accessory SKUs must be unique
3. **Required Fields**: Products must have SKU, name, and price
4. **Price Validation**: Prices must be positive numbers

## File Upload Format

For bulk uploads, use this format:

```csv
sku,name,price,description,category,base_product
HP-T120-24,HP DesignJet T120 24-inch,999.99,24-inch plotter,Plotters,true
HP-STAND-T120,HP Stand for T120,199.99,Adjustable stand,,false
```

## Error Handling

The application includes comprehensive error handling:
- API connection errors are displayed to users
- Database constraint violations are caught and reported
- File upload errors are validated and shown
- Compatibility violations prevent invalid quote configurations

## Development

To extend the application:

1. **Add New Features**: Modify the FastAPI endpoints in `api.py`
2. **Update UI**: Modify the Streamlit interface in `frontend.py`
3. **Database Changes**: Update the schema in `database.py`
4. **Sample Data**: Modify `sample_data.py` for testing

## Troubleshooting

**Common Issues:**

1. **"Cannot connect to API"**: Make sure the FastAPI server is running on port 8000
2. **Database errors**: Try deleting `sales_quotes.db` and running `python sample_data.py`
3. **Port conflicts**: Change ports in the startup scripts if needed
4. **Import errors**: Install all requirements with `pip install -r requirements.txt`