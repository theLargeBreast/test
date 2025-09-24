"""Streamlit frontend for the sales quoting application."""

import streamlit as st
import pandas as pd
import requests
import json
from typing import Dict, List, Any
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Sales Quoting System",
    page_icon="💰",
    layout="wide"
)

def call_api(endpoint: str, method: str = "GET", data: Dict = None, files: Dict = None) -> Dict:
    """Make API calls to the FastAPI backend."""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files)
            else:
                response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url, json=data)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return {}
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Make sure the FastAPI server is running on port 8000.")
        return {}
    except Exception as e:
        st.error(f"Error calling API: {str(e)}")
        return {}

def main():
    """Main Streamlit application."""
    st.title("💰 Sales Quoting System")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Product Management", "Accessory Management", "Compatibility Rules", "Quote Builder", "Bulk Upload"]
    )
    
    if page == "Product Management":
        product_management_page()
    elif page == "Accessory Management":
        accessory_management_page()
    elif page == "Compatibility Rules":
        compatibility_rules_page()
    elif page == "Quote Builder":
        quote_builder_page()
    elif page == "Bulk Upload":
        bulk_upload_page()

def product_management_page():
    """Product management interface."""
    st.header("🏷️ Product Management")
    
    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["View Products", "Add Product", "Edit/Delete Product"])
    
    with tab1:
        st.subheader("All Products")
        products = call_api("/products")
        
        if products:
            df = pd.DataFrame(products)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No products found.")
    
    with tab2:
        st.subheader("Add New Product")
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                sku = st.text_input("SKU*", placeholder="Enter unique SKU")
                name = st.text_input("Product Name*", placeholder="Enter product name")
                price = st.number_input("Price*", min_value=0.01, step=0.01)
                
            with col2:
                description = st.text_area("Description", placeholder="Product description")
                category = st.text_input("Category", placeholder="Product category")
                base_product = st.checkbox("Base Product", help="Check if this is a base product that can have accessories")
            
            submitted = st.form_submit_button("Add Product")
            
            if submitted and sku and name and price > 0:
                product_data = {
                    "sku": sku,
                    "name": name,
                    "price": price,
                    "description": description,
                    "category": category,
                    "base_product": base_product
                }
                
                result = call_api("/products", method="POST", data=product_data)
                if result:
                    st.success("Product added successfully!")
                    st.rerun()
            elif submitted:
                st.error("Please fill in all required fields (marked with *).")
    
    with tab3:
        st.subheader("Edit/Delete Product")
        
        products = call_api("/products")
        if products:
            product_options = {f"{p['sku']} - {p['name']}": p['sku'] for p in products}
            selected_product = st.selectbox("Select Product", list(product_options.keys()))
            
            if selected_product:
                sku = product_options[selected_product]
                product = call_api(f"/products/{sku}")
                
                if product:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        with st.form("edit_product_form"):
                            st.write(f"Editing: {product['sku']}")
                            
                            new_name = st.text_input("Product Name", value=product['name'])
                            new_price = st.number_input("Price", value=float(product['price']), min_value=0.01, step=0.01)
                            new_description = st.text_area("Description", value=product.get('description', ''))
                            new_category = st.text_input("Category", value=product.get('category', ''))
                            new_base_product = st.checkbox("Base Product", value=bool(product.get('base_product', False)))
                            
                            if st.form_submit_button("Update Product"):
                                update_data = {
                                    "sku": sku,  # Keep original SKU
                                    "name": new_name,
                                    "price": new_price,
                                    "description": new_description,
                                    "category": new_category,
                                    "base_product": new_base_product
                                }
                                
                                result = call_api(f"/products/{sku}", method="PUT", data=update_data)
                                if result:
                                    st.success("Product updated successfully!")
                                    st.rerun()
                    
                    with col2:
                        st.write("⚠️ **Danger Zone**")
                        if st.button("Delete Product", type="secondary"):
                            result = call_api(f"/products/{sku}", method="DELETE")
                            if result:
                                st.success("Product deleted successfully!")
                                st.rerun()

def accessory_management_page():
    """Accessory management interface."""
    st.header("🔧 Accessory Management")
    
    tab1, tab2 = st.tabs(["View Accessories", "Add Accessory"])
    
    with tab1:
        st.subheader("All Accessories")
        accessories = call_api("/accessories")
        
        if accessories:
            df = pd.DataFrame(accessories)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No accessories found.")
    
    with tab2:
        st.subheader("Add New Accessory")
        
        with st.form("add_accessory_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                sku = st.text_input("SKU*", placeholder="Enter unique SKU")
                name = st.text_input("Accessory Name*", placeholder="Enter accessory name")
                
            with col2:
                price = st.number_input("Price*", min_value=0.01, step=0.01)
                description = st.text_area("Description", placeholder="Accessory description")
            
            submitted = st.form_submit_button("Add Accessory")
            
            if submitted and sku and name and price > 0:
                accessory_data = {
                    "sku": sku,
                    "name": name,
                    "price": price,
                    "description": description
                }
                
                result = call_api("/accessories", method="POST", data=accessory_data)
                if result:
                    st.success("Accessory added successfully!")
                    st.rerun()
            elif submitted:
                st.error("Please fill in all required fields (marked with *).")

def compatibility_rules_page():
    """Compatibility rules management interface."""
    st.header("🔗 Compatibility Rules")
    st.write("Define which accessories are compatible with which base products.")
    
    tab1, tab2 = st.tabs(["Add Rule", "View Compatible Accessories"])
    
    with tab1:
        st.subheader("Add Compatibility Rule")
        
        # Get base products and accessories
        products = call_api("/products")
        accessories = call_api("/accessories")
        
        base_products = [p for p in products if p.get('base_product', False)]
        
        if base_products and accessories:
            with st.form("add_rule_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    base_options = {f"{p['sku']} - {p['name']}": p['sku'] for p in base_products}
                    selected_base = st.selectbox("Base Product", list(base_options.keys()))
                
                with col2:
                    acc_options = {f"{a['sku']} - {a['name']}": a['sku'] for a in accessories}
                    selected_acc = st.selectbox("Accessory", list(acc_options.keys()))
                
                if st.form_submit_button("Add Compatibility Rule"):
                    if selected_base and selected_acc:
                        rule_data = {
                            "base_product_sku": base_options[selected_base],
                            "accessory_sku": acc_options[selected_acc]
                        }
                        
                        result = call_api("/compatibility-rules", method="POST", data=rule_data)
                        if result:
                            st.success("Compatibility rule added successfully!")
                            st.rerun()
        else:
            st.warning("You need at least one base product and one accessory to create compatibility rules.")
    
    with tab2:
        st.subheader("View Compatible Accessories")
        
        products = call_api("/products")
        base_products = [p for p in products if p.get('base_product', False)]
        
        if base_products:
            base_options = {f"{p['sku']} - {p['name']}": p['sku'] for p in base_products}
            selected_base = st.selectbox("Select Base Product to View Compatible Accessories", 
                                       list(base_options.keys()), key="view_compat")
            
            if selected_base:
                sku = base_options[selected_base]
                compatible_accessories = call_api(f"/products/{sku}/compatible-accessories")
                
                if compatible_accessories:
                    df = pd.DataFrame(compatible_accessories)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No compatible accessories found for this base product.")

def quote_builder_page():
    """Quote builder interface."""
    st.header("📝 Quote Builder")
    
    # Initialize session state for cart
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    if 'quote_number' not in st.session_state:
        st.session_state.quote_number = f"Q{int(time.time())}"
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Add Items to Quote")
        
        # Quote information
        st.session_state.quote_number = st.text_input("Quote Number", value=st.session_state.quote_number)
        customer_name = st.text_input("Customer Name")
        
        # Add products/accessories
        tab1, tab2 = st.tabs(["Add Products", "Add Accessories"])
        
        with tab1:
            products = call_api("/products")
            if products:
                product_options = {f"{p['sku']} - {p['name']} (${p['price']})": p for p in products}
                selected_product = st.selectbox("Select Product", list(product_options.keys()))
                quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
                
                if st.button("Add Product to Cart"):
                    product = product_options[selected_product]
                    cart_item = {
                        'sku': product['sku'],
                        'name': product['name'],
                        'quantity': quantity,
                        'unit_price': product['price'],
                        'line_total': quantity * product['price'],
                        'item_type': 'product'
                    }
                    st.session_state.cart.append(cart_item)
                    st.success(f"Added {quantity}x {product['name']} to cart!")
                    st.rerun()
        
        with tab2:
            # Show compatible accessories based on products in cart
            base_products_in_cart = [item for item in st.session_state.cart if item['item_type'] == 'product']
            
            if base_products_in_cart:
                st.write("Compatible accessories for products in your cart:")
                
                all_compatible_accessories = []
                for base_product in base_products_in_cart:
                    compatible = call_api(f"/products/{base_product['sku']}/compatible-accessories")
                    all_compatible_accessories.extend(compatible)
                
                # Remove duplicates
                unique_accessories = {acc['sku']: acc for acc in all_compatible_accessories}.values()
                
                if unique_accessories:
                    acc_options = {f"{a['sku']} - {a['name']} (${a['price']})": a for a in unique_accessories}
                    selected_acc = st.selectbox("Select Accessory", list(acc_options.keys()))
                    acc_quantity = st.number_input("Accessory Quantity", min_value=1, value=1, step=1, key="acc_qty")
                    
                    if st.button("Add Accessory to Cart"):
                        accessory = acc_options[selected_acc]
                        cart_item = {
                            'sku': accessory['sku'],
                            'name': accessory['name'],
                            'quantity': acc_quantity,
                            'unit_price': accessory['price'],
                            'line_total': acc_quantity * accessory['price'],
                            'item_type': 'accessory'
                        }
                        st.session_state.cart.append(cart_item)
                        st.success(f"Added {acc_quantity}x {accessory['name']} to cart!")
                        st.rerun()
                else:
                    st.info("No compatible accessories found for products in cart.")
            else:
                st.info("Add base products first to see compatible accessories.")
    
    with col2:
        st.subheader("🛒 Cart")
        
        if st.session_state.cart:
            total = 0
            for i, item in enumerate(st.session_state.cart):
                with st.container():
                    st.write(f"**{item['name']}** ({item['sku']})")
                    st.write(f"Qty: {item['quantity']} × ${item['unit_price']:.2f} = ${item['line_total']:.2f}")
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.cart.pop(i)
                        st.rerun()
                    st.write("---")
                    total += item['line_total']
            
            st.write(f"### **Total: ${total:.2f}**")
            
            col_clear, col_save = st.columns(2)
            with col_clear:
                if st.button("Clear Cart"):
                    st.session_state.cart = []
                    st.rerun()
            
            with col_save:
                if st.button("Save Quote"):
                    # Prepare quote data
                    quote_items = [
                        {
                            "sku": item['sku'],
                            "quantity": item['quantity'],
                            "item_type": item['item_type']
                        }
                        for item in st.session_state.cart
                    ]
                    
                    quote_data = {
                        "quote_number": st.session_state.quote_number,
                        "customer_name": customer_name,
                        "items": quote_items
                    }
                    
                    result = call_api("/quotes", method="POST", data=quote_data)
                    if result:
                        st.success("Quote saved successfully!")
                        st.session_state.cart = []
                        st.session_state.quote_number = f"Q{int(time.time())}"
                        st.rerun()
        else:
            st.info("Cart is empty. Add some products!")

def bulk_upload_page():
    """Bulk upload interface."""
    st.header("📤 Bulk Upload")
    
    st.write("Upload products in bulk using CSV or Excel files.")
    
    # Show expected format
    with st.expander("Expected File Format"):
        st.write("Your file should contain the following columns:")
        sample_data = {
            "sku": ["HP-PLOTTER-1", "HP-PLOTTER-2"],
            "name": ["HP DesignJet T120", "HP DesignJet T520"],
            "price": [999.99, 1499.99],
            "description": ["24-inch plotter", "36-inch plotter"],
            "category": ["Plotters", "Plotters"],
            "base_product": [True, True]
        }
        st.dataframe(pd.DataFrame(sample_data))
        st.write("**Required columns:** sku, name, price")
        st.write("**Optional columns:** description, category, base_product")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload a CSV or Excel file with product data"
    )
    
    if uploaded_file is not None:
        # Preview file
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write("### File Preview")
            st.dataframe(df.head())
            
            # Validate required columns
            required_columns = ['sku', 'name', 'price']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Missing required columns: {missing_columns}")
            else:
                st.success("File format looks good!")
                
                if st.button("Upload Products"):
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    result = call_api("/bulk-upload/products", method="POST", files=files)
                    
                    if result:
                        st.success(f"Upload completed! {result['successful_imports']} out of {result['total_rows']} products imported.")
                        
                        if result.get('errors'):
                            st.warning("Some rows had errors:")
                            for error in result['errors']:
                                st.write(f"- {error}")
        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

if __name__ == "__main__":
    main()