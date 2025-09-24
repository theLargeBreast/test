#!/usr/bin/env python3
"""Script to populate the database with sample data."""

from database import init_database, ProductDB, AccessoryDB, CompatibilityDB

def populate_sample_data():
    """Populate database with sample products, accessories, and rules."""
    
    print("Initializing database...")
    init_database()
    
    print("Adding sample products...")
    
    # Add sample base products (HP Plotters)
    products_data = [
        {
            "sku": "HP-T120-24",
            "name": "HP DesignJet T120 24-inch",
            "price": 999.99,
            "description": "24-inch large format printer for technical drawings",
            "category": "Plotters",
            "base_product": True
        },
        {
            "sku": "HP-T520-36",
            "name": "HP DesignJet T520 36-inch", 
            "price": 1499.99,
            "description": "36-inch large format printer for CAD and GIS applications",
            "category": "Plotters",
            "base_product": True
        },
        {
            "sku": "HP-T730-36",
            "name": "HP DesignJet T730 36-inch",
            "price": 2299.99,
            "description": "36-inch printer with built-in scanner for technical workflows",
            "category": "Plotters",
            "base_product": True
        }
    ]
    
    for product in products_data:
        try:
            ProductDB.create_product(**product)
            print(f"Added product: {product['name']}")
        except Exception as e:
            print(f"Error adding product {product['sku']}: {e}")
    
    print("\nAdding sample accessories...")
    
    # Add sample accessories
    accessories_data = [
        {
            "sku": "HP-STAND-T120",
            "name": "HP Stand for T120 Series",
            "price": 199.99,
            "description": "Adjustable stand for HP T120 plotters"
        },
        {
            "sku": "HP-STAND-T520",
            "name": "HP Stand for T520/T730 Series", 
            "price": 299.99,
            "description": "Heavy-duty stand for HP T520 and T730 plotters"
        },
        {
            "sku": "HP-PAPER-ROLL-24",
            "name": "HP Paper Roll 24-inch",
            "price": 45.99,
            "description": "24-inch bond paper roll, 150 feet"
        },
        {
            "sku": "HP-PAPER-ROLL-36",
            "name": "HP Paper Roll 36-inch",
            "price": 65.99, 
            "description": "36-inch bond paper roll, 150 feet"
        },
        {
            "sku": "HP-INK-BLACK",
            "name": "HP Black Ink Cartridge",
            "price": 89.99,
            "description": "High-capacity black ink cartridge"
        },
        {
            "sku": "HP-INK-COLOR",
            "name": "HP Color Ink Set",
            "price": 199.99,
            "description": "Complete color ink cartridge set (C/M/Y)"
        }
    ]
    
    for accessory in accessories_data:
        try:
            AccessoryDB.create_accessory(**accessory)
            print(f"Added accessory: {accessory['name']}")
        except Exception as e:
            print(f"Error adding accessory {accessory['sku']}: {e}")
    
    print("\nAdding compatibility rules...")
    
    # Add compatibility rules
    compatibility_rules = [
        # T120 compatible accessories
        ("HP-T120-24", "HP-STAND-T120"),
        ("HP-T120-24", "HP-PAPER-ROLL-24"),
        ("HP-T120-24", "HP-INK-BLACK"),
        ("HP-T120-24", "HP-INK-COLOR"),
        
        # T520 compatible accessories  
        ("HP-T520-36", "HP-STAND-T520"),
        ("HP-T520-36", "HP-PAPER-ROLL-36"),
        ("HP-T520-36", "HP-INK-BLACK"),
        ("HP-T520-36", "HP-INK-COLOR"),
        
        # T730 compatible accessories
        ("HP-T730-36", "HP-STAND-T520"),
        ("HP-T730-36", "HP-PAPER-ROLL-36"), 
        ("HP-T730-36", "HP-INK-BLACK"),
        ("HP-T730-36", "HP-INK-COLOR"),
    ]
    
    for base_sku, acc_sku in compatibility_rules:
        try:
            CompatibilityDB.add_compatibility_rule(base_sku, acc_sku)
            print(f"Added rule: {base_sku} -> {acc_sku}")
        except Exception as e:
            print(f"Error adding rule {base_sku} -> {acc_sku}: {e}")
    
    print("\n✅ Sample data population completed!")
    print("\nSample products added:")
    print("- HP DesignJet T120 24-inch ($999.99)")
    print("- HP DesignJet T520 36-inch ($1,499.99)")
    print("- HP DesignJet T730 36-inch ($2,299.99)")
    
    print("\nSample accessories added:")
    print("- Stands, paper rolls, and ink cartridges")
    print("- Each with appropriate compatibility rules")

if __name__ == "__main__":
    populate_sample_data()