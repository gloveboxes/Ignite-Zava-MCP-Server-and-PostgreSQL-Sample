"""
Customer Sales Database Generator for SQLite

This script generates a comprehensive customer sales database with optimized indexing
for SQLite.

DATA FILE STRUCTURE (all in reference_data/ folder):
- stores_reference.json: Consolidated store configurations, product assignments, and seasonal data
- product_data.json: Contains all product information (main_categories with products)
- supplier_data.json: Contains supplier information for clothing/apparel vendors
- seasonal_multipliers.json: Contains seasonal adjustment factors for different climate zones

SQLITE CONNECTION:
- Uses sqlite3 module (built-in)
- Creates or connects to retail.db SQLite database file
- Targets all tables in the database (no schema concept in SQLite)

FEATURES:
- Complete database generation with customers, products, stores, orders
- Product image embeddings population from product_data.json
- Product description embeddings population from product_data.json
- Performance-optimized indexes
- Comprehensive statistics and verification
- Reproducible store product assignments (via store_products.json)

USAGE:
    python generate_github_sqlite.py                     # Generate complete database
    python generate_github_sqlite.py --show-stats        # Show database statistics
    python generate_github_sqlite.py --embeddings-only   # Populate embeddings only
    python generate_github_sqlite.py --verify-embeddings # Verify embeddings table
    python generate_github_sqlite.py --help              # Show all options
"""

import json
import logging
import os
import random
import sqlite3
from datetime import date, timedelta
from typing import List, Tuple

from dotenv import load_dotenv
from faker import Faker

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
env_paths = [
    os.path.join(script_dir, '.env'),
    os.path.join(script_dir, '..', '..', '..', '.env'),
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break
else:
    load_dotenv()

# Initialize Faker and logging
fake = Faker()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Reference data file constants
REFERENCE_DATA_DIR = 'reference_data'
STORES_REFERENCE_FILE = 'stores_reference.json'
PRODUCT_DATA_FILE = 'product_data.json'
SUPPLIER_DATA_FILE = 'supplier_data.json'
SEASONAL_MULTIPLIERS_FILE = 'seasonal_multipliers.json'

# SQLite configuration
# Create database in parent /data folder
SQLITE_DB_FILE = os.getenv('SQLITE_DB_FILE', os.path.join(os.path.dirname(__file__), '..', 'retail.db'))

# Super Manager UUID - has access to all rows
SUPER_MANAGER_UUID = '00000000-0000-0000-0000-000000000000'

# Load reference data from JSON file
def load_reference_data():
    """Load reference data from consolidated stores_reference.json file"""
    try:
        consolidated_path = os.path.join(os.path.dirname(__file__), REFERENCE_DATA_DIR, STORES_REFERENCE_FILE)
        with open(consolidated_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load {REFERENCE_DATA_DIR}/{STORES_REFERENCE_FILE}: {e}")
        raise

def load_seasonal_multipliers():
    """Load seasonal multipliers configuration"""
    try:
        seasonal_path = os.path.join(os.path.dirname(__file__), REFERENCE_DATA_DIR, SEASONAL_MULTIPLIERS_FILE)
        with open(seasonal_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.warning(f"Failed to load seasonal multipliers: {e}")
        return None

def load_product_data():
    """Load product data from JSON file"""
    try:
        json_path = os.path.join(os.path.dirname(__file__), REFERENCE_DATA_DIR, PRODUCT_DATA_FILE)
        with open(json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load product data: {e}")
        raise

# Load the reference data
reference_data = load_reference_data()
product_data = load_product_data()
seasonal_config = load_seasonal_multipliers()

# Get reference data from loaded JSON
main_categories = product_data['main_categories']
stores = reference_data['stores']

# Global variable for supplier category mapping
SUPPLIER_CATEGORY_MAP = {}

def get_store_name_from_id(store_id: str) -> str:
    """Get store name from store ID"""
    if store_id in stores:
        return stores[store_id].get('store_name', store_id)
    return store_id

def get_store_id_from_name(store_name: str) -> str:
    """Get store ID from store name"""
    for store_id, config in stores.items():
        if config.get('store_name') == store_name:
            return store_id
    return store_name

def is_using_store_ids() -> bool:
    """Check if we're using the new ID-based format"""
    first_store_key = next(iter(stores.keys()))
    return 'store_name' in stores[first_store_key]

def weighted_store_choice():
    """Choose a store based on weighted distribution"""
    store_keys = list(stores.keys())
    weights = [stores[store]['customer_distribution_weight'] for store in store_keys]
    selected_key = random.choices(store_keys, weights=weights, k=1)[0]
    
    if is_using_store_ids():
        return get_store_name_from_id(selected_key)
    else:
        return selected_key

def generate_phone_number(region=None):
    """Generate a phone number in North American format (XXX) XXX-XXXX"""
    return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"

def get_seasonal_multipliers_for_store_and_category(store_name: str, category: str) -> List[float]:
    """Get seasonal multipliers for a specific store and category"""
    try:
        store_config = None
        if is_using_store_ids():
            store_id = get_store_id_from_name(store_name)
            store_config = stores.get(store_id, {})
        else:
            store_config = stores.get(store_name, {})
        
        if not store_config:
            logging.warning(f"Store config not found for {store_name}")
            return [1.0] * 12
        
        if seasonal_config and 'climate_zones' in seasonal_config:
            location = store_config.get('location', {})
            climate_zone = location.get('climate_zone', 'temperate')
            
            climate_zones = seasonal_config.get('climate_zones', {})
            zone_config = climate_zones.get(climate_zone, {})
            category_multipliers = zone_config.get('categories', {})
            
            return category_multipliers.get(category, [1.0] * 12)
        
        if 'seasonal_multipliers' in reference_data:
            location = store_config.get('location', {})
            climate_zone = location.get('climate_zone', 'temperate')
            
            if climate_zone in reference_data['seasonal_multipliers']:
                return reference_data['seasonal_multipliers'][climate_zone]
        
        return [1.0] * 12
    except Exception as e:
        logging.warning(f"Error getting seasonal multipliers for {store_name}/{category}: {e}")
        return [1.0] * 12

def create_connection():
    """Create SQLite database connection"""
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        logging.info(f"Connected to SQLite database: {SQLITE_DB_FILE}")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to SQLite: {e}")
        raise

def create_database_schema(conn):
    """Create database schema from SQL file"""
    try:
        logging.info("Loading database schema from SQL file...")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file_path = os.path.join(script_dir, "github_retail_schema_sqlite.sql")
        
        if not os.path.exists(sql_file_path):
            raise FileNotFoundError(f"Schema SQL file not found at: {sql_file_path}")
        
        with open(sql_file_path, 'r') as f:
            sql_script = f.read()
        
        # Execute the SQL script
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()
        
        logging.info("Database schema created successfully from SQL file!")
        
    except Exception as e:
        logging.error(f"Error creating database schema: {e}")
        raise

def batch_insert(conn, query: str, data: List[Tuple], batch_size: int = 1000):
    """Insert data in batches"""
    cursor = conn.cursor()
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        cursor.executemany(query, batch)
    conn.commit()

def insert_customers(conn, num_customers: int = 100000):
    """Insert customer data into the database"""
    try:
        logging.info(f"Generating {num_customers:,} customers...")
        
        cursor = conn.cursor()
        cursor.execute("SELECT store_id, store_name FROM stores")
        store_rows = cursor.fetchall()
        store_ids = [row[0] for row in store_rows]
        
        if not store_ids:
            raise Exception("No stores found! Please insert stores first.")
        
        customers_data = []
        
        for i in range(1, num_customers + 1):
            first_name = fake.first_name().replace("'", "''")
            last_name = fake.last_name().replace("'", "''")
            email = f"{first_name.lower()}.{last_name.lower()}.{i}@example.com"
            phone = generate_phone_number()
            
            preferred_store_name = weighted_store_choice()
            primary_store_id = None
            for store_id, store_name in store_rows:
                if store_name == preferred_store_name:
                    primary_store_id = store_id
                    break
            
            if primary_store_id is None:
                primary_store_id = store_rows[0][0]
            
            customers_data.append((first_name, last_name, email, phone, primary_store_id))
        
        batch_insert(conn, 
            "INSERT INTO customers (first_name, last_name, email, phone, primary_store_id) VALUES (?, ?, ?, ?, ?)", 
            customers_data)
        
        # Log customer distribution by store
        cursor.execute("""
            SELECT s.store_name, COUNT(c.customer_id) as customer_count,
                   ROUND(100.0 * COUNT(c.customer_id) / ?, 1) as percentage
            FROM stores s
            LEFT JOIN customers c ON s.store_id = c.primary_store_id
            GROUP BY s.store_id, s.store_name
            ORDER BY customer_count DESC
        """, (num_customers,))
        distribution = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM customers WHERE primary_store_id IS NULL")
        no_store_count = cursor.fetchone()[0]
        
        logging.info("Customer distribution by store:")
        for store_name, customer_count, percentage in distribution:
            logging.info(f"  {store_name}: {customer_count:,} customers ({percentage}%)")
        if no_store_count > 0:
            logging.info(f"  No primary store: {no_store_count:,} customers ({100.0 * no_store_count / num_customers:.1f}%)")
        else:
            logging.info("  ✅ All customers have been assigned to stores!")
        
        logging.info(f"Successfully inserted {num_customers:,} customers!")
    except Exception as e:
        logging.error(f"Error inserting customers: {e}")
        raise

def insert_stores(conn):
    """Insert store data into the database"""
    try:
        logging.info("Generating stores...")
        
        stores_data = []
        
        for store_key, store_config in stores.items():
            if is_using_store_ids():
                store_name = store_config.get('store_name', store_key)
            else:
                store_name = store_key
            
            is_online = 1 if "online" in store_name.lower() else 0
            rls_user_id = store_config.get('rls_user_id')
            if not rls_user_id:
                raise ValueError(f"No rls_user_id found for store: {store_name}")
            stores_data.append((store_name, rls_user_id, is_online))
        
        batch_insert(conn, 
            "INSERT INTO stores (store_name, rls_user_id, is_online) VALUES (?, ?, ?)", 
            stores_data)
        
        cursor = conn.cursor()
        cursor.execute("SELECT store_name, rls_user_id FROM stores ORDER BY store_name")
        rows = cursor.fetchall()
        logging.info("Store Manager IDs (for workshop use):")
        for store_name, rls_user_id in rows:
            logging.info(f"  {store_name}: {rls_user_id}")
        
        logging.info(f"Successfully inserted {len(stores_data):,} stores!")
    except Exception as e:
        logging.error(f"Error inserting stores: {e}")
        raise

def insert_categories(conn):
    """Insert category data into the database"""
    try:
        logging.info("Generating categories...")
        
        categories_data = []
        
        for main_category in main_categories.keys():
            categories_data.append((main_category,))
        
        batch_insert(conn, 
            "INSERT INTO categories (category_name) VALUES (?)", 
            categories_data)
        
        logging.info(f"Successfully inserted {len(categories_data):,} categories!")
    except Exception as e:
        logging.error(f"Error inserting categories: {e}")
        raise

def insert_product_types(conn):
    """Insert product type data into the database"""
    try:
        logging.info("Generating product types...")
        
        cursor = conn.cursor()
        cursor.execute("SELECT category_id, category_name FROM categories")
        category_rows = cursor.fetchall()
        
        category_mapping = {}
        for category_id, category_name in category_rows:
            category_mapping[category_name] = category_id
        
        product_types_data = []
        
        for main_category, subcategories in main_categories.items():
            category_id = category_mapping[main_category]
            for subcategory in subcategories.keys():
                product_types_data.append((category_id, subcategory))
        
        batch_insert(conn, 
            "INSERT INTO product_types (category_id, type_name) VALUES (?, ?)", 
            product_types_data)
        
        logging.info(f"Successfully inserted {len(product_types_data):,} product types!")
    except Exception as e:
        logging.error(f"Error inserting product types: {e}")
        raise

def insert_suppliers(conn):
    """Insert supplier data into the database from JSON file"""
    try:
        logging.info(f"Loading suppliers from {SUPPLIER_DATA_FILE}...")
        
        supplier_json_path = os.path.join(os.path.dirname(__file__), REFERENCE_DATA_DIR, SUPPLIER_DATA_FILE)
        
        if not os.path.exists(supplier_json_path):
            raise FileNotFoundError(f"Supplier data file not found: {supplier_json_path}")
        
        with open(supplier_json_path, 'r') as f:
            supplier_config = json.load(f)
        
        if 'suppliers' in supplier_config:
            suppliers_from_json = supplier_config['suppliers']
        else:
            suppliers_from_json = [supplier_config[key] for key in supplier_config.keys() if key.isdigit()]
        
        if not suppliers_from_json:
            raise ValueError(f"No suppliers found in {SUPPLIER_DATA_FILE}")
        
        logging.info(f"Loaded {len(suppliers_from_json)} suppliers from JSON file")
        
        supplier_insert_data = []
        for idx, supplier in enumerate(suppliers_from_json, 1):
            supplier_code = supplier.get('supplier_code', f"SUP{idx:03d}")
            
            address = supplier.get('address', '')
            address_parts = address.split(',') if address else []
            
            address_line1 = address_parts[0].strip() if len(address_parts) > 0 else ''
            city = address_parts[1].strip() if len(address_parts) > 1 else 'Seattle'
            
            if len(address_parts) > 2:
                state_postal = address_parts[2].strip().split()
                state = state_postal[0] if len(state_postal) > 0 else 'WA'
                postal_code = state_postal[1] if len(state_postal) > 1 else '98000'
            else:
                state = 'WA'
                postal_code = '98000'
            
            min_order = supplier.get('min_order_amount', 500.00)
            bulk_threshold = min_order * 5
            bulk_discount = random.uniform(5.0, 10.0)
            
            rating = supplier.get('rating', 4.0)
            is_preferred = supplier.get('is_preferred', rating >= 4.5)
            approved_vendor = 1
            esg_compliant = 1 if is_preferred else 0
            
            supplier_id = supplier.get('supplier_id', idx)
            
            supplier_insert_data.append((
                supplier_id,
                supplier.get('name', f'Supplier {idx}'),
                supplier_code,
                supplier.get('email', f'contact{idx}@supplier.com'),
                supplier.get('phone', f'(555) {idx:03d}-0000'),
                address_line1,
                '',
                city,
                state,
                postal_code,
                'USA',
                supplier.get('payment_terms', 'Net 30'),
                supplier.get('lead_time_days', 14),
                min_order,
                bulk_threshold,
                bulk_discount,
                rating,
                esg_compliant,
                approved_vendor,
                1 if is_preferred else 0
            ))
        
        logging.info(f"Prepared {len(supplier_insert_data)} suppliers for insertion...")
        
        batch_insert(conn, """
            INSERT INTO suppliers (
                supplier_id, supplier_name, supplier_code, contact_email, contact_phone,
                address_line1, address_line2, city, state_province, postal_code, country,
                payment_terms, lead_time_days, minimum_order_amount, bulk_discount_threshold, bulk_discount_percent,
                supplier_rating, esg_compliant, approved_vendor, preferred_vendor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, supplier_insert_data)
        
        logging.info(f"Successfully inserted {len(supplier_insert_data):,} suppliers!")
        
        # Store category and product type mappings
        global SUPPLIER_CATEGORY_MAP
        SUPPLIER_CATEGORY_MAP = {}
        for supplier in suppliers_from_json:
            supplier_name = supplier.get('name', '')
            categories = supplier.get('categories', [])
            product_types = supplier.get('product_types', [])
            
            for category in categories:
                if category not in SUPPLIER_CATEGORY_MAP:
                    SUPPLIER_CATEGORY_MAP[category] = []
                SUPPLIER_CATEGORY_MAP[category].append(supplier_name)
            
            for product_type in product_types:
                product_key = f"product_type:{product_type}"
                if product_key not in SUPPLIER_CATEGORY_MAP:
                    SUPPLIER_CATEGORY_MAP[product_key] = []
                SUPPLIER_CATEGORY_MAP[product_key].append(supplier_name)
        
        # Insert initial supplier performance data
        logging.info("Generating supplier performance evaluations...")
        
        cursor = conn.cursor()
        cursor.execute("SELECT supplier_id, supplier_name FROM suppliers")
        supplier_rows = cursor.fetchall()
        
        performance_data = []
        for supplier_id, supplier_name in supplier_rows:
            for months_ago in range(0, random.randint(3, 7)):
                evaluation_date = date.today().replace(day=1) - timedelta(days=months_ago * 30)
                
                base_cost_score = random.uniform(3.5, 4.8)
                base_quality_score = random.uniform(3.2, 4.9)
                base_delivery_score = random.uniform(3.0, 4.7)
                base_compliance_score = random.uniform(4.2, 5.0)
                
                cost_score = max(1.0, min(5.0, base_cost_score + random.uniform(-0.3, 0.3)))
                quality_score = max(1.0, min(5.0, base_quality_score + random.uniform(-0.4, 0.4)))
                delivery_score = max(1.0, min(5.0, base_delivery_score + random.uniform(-0.5, 0.5)))
                compliance_score = max(1.0, min(5.0, base_compliance_score + random.uniform(-0.2, 0.2)))
                
                overall_score = (cost_score * 0.3 + quality_score * 0.3 + delivery_score * 0.25 + compliance_score * 0.15)
                
                performance_data.append((
                    supplier_id, evaluation_date, cost_score, quality_score,
                    delivery_score, compliance_score, overall_score,
                    f"Monthly evaluation for {supplier_name}"
                ))
        
        batch_insert(conn, """
            INSERT INTO supplier_performance (
                supplier_id, evaluation_date, cost_score, quality_score,
                delivery_score, compliance_score, overall_score, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, performance_data)
        
        logging.info(f"Successfully inserted {len(performance_data):,} supplier performance evaluations!")
        
    except Exception as e:
        logging.error(f"Error inserting suppliers: {e}")
        raise

def insert_products(conn):
    """Insert product data into the database"""
    try:
        logging.info("Generating products...")
        
        cursor = conn.cursor()
        
        cursor.execute("SELECT category_id, category_name FROM categories")
        category_rows = cursor.fetchall()
        category_mapping = {cat_name: cat_id for cat_id, cat_name in category_rows}
        
        cursor.execute("SELECT type_id, type_name, category_id FROM product_types")
        type_rows = cursor.fetchall()
        type_mapping = {type_name: (type_id, cat_id) for type_id, type_name, cat_id in type_rows}
        
        cursor.execute("SELECT supplier_id, supplier_name, preferred_vendor FROM suppliers ORDER BY preferred_vendor DESC, supplier_rating DESC")
        supplier_rows = cursor.fetchall()
        
        if not supplier_rows:
            raise Exception("No suppliers found!")
        
        supplier_by_name = {s[1]: s[0] for s in supplier_rows}
        default_suppliers = supplier_rows[:5]
        
        products_data = []
        sku_counter = 1000
        
        for main_category, subcategories in main_categories.items():
            category_id = category_mapping[main_category]
            
            for subcategory, products in subcategories.items():
                type_id, _ = type_mapping[subcategory]
                
                # Get suppliers for this category
                category_suppliers = SUPPLIER_CATEGORY_MAP.get(main_category, [])
                
                for product in products:
                    sku_counter += 1
                    sku = f"SKU{sku_counter}"
                    
                    # Find supplier
                    supplier_id = None
                    if category_suppliers:
                        supplier_name = random.choice(category_suppliers)
                        supplier_id = supplier_by_name.get(supplier_name)
                    
                    if not supplier_id:
                        supplier_id = random.choice(default_suppliers)[0]
                    
                    cost = round(random.uniform(10.0, 500.0), 2)
                    markup = random.uniform(1.5, 3.0)
                    base_price = round(cost * markup, 2)
                    
                    products_data.append((
                        sku,
                        product.get('name', f'Product {sku_counter}'),
                        category_id,
                        type_id,
                        supplier_id,
                        cost,
                        base_price,
                        33.00,
                        product.get('description', ''),
                        random.randint(7, 30),
                        random.randint(1, 50),
                        0
                    ))
        
        batch_insert(conn, """
            INSERT INTO products (
                sku, product_name, category_id, type_id, supplier_id, cost, base_price,
                gross_margin_percent, product_description, procurement_lead_time_days,
                minimum_order_quantity, discontinued
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, products_data)
        
        logging.info(f"Successfully inserted {len(products_data):,} products!")
    except Exception as e:
        logging.error(f"Error inserting products: {e}")
        raise

def insert_agent_support_data(conn):
    """Insert agent support data (approvers, contracts, policies, procurement requests, notifications)"""
    try:
        logging.info("Generating essential agent support data...")
        
        cursor = conn.cursor()
        
        # Generate approvers
        approvers_data = [
            ("EXEC001", "Jane CEO", "jane.ceo@company.com", "Management", 1000000, 1),
            ("DIR001", "John Finance Director", "john.director@company.com", "Finance", 250000, 1),
            ("DIR002", "Sarah Operations Director", "sarah.ops@company.com", "Operations", 200000, 1),
            ("MGR001", "Mike Procurement Manager", "mike.proc@company.com", "Procurement", 50000, 1),
            ("MGR002", "Lisa Finance Manager", "lisa.fin@company.com", "Finance", 25000, 1),
            ("SUP001", "Tom Operations Supervisor", "tom.ops@company.com", "Operations", 10000, 1),
            ("SUP002", "Amy Procurement Specialist", "amy.proc@company.com", "Procurement", 5000, 1)
        ]
        
        batch_insert(conn, """
            INSERT INTO approvers (
                employee_id, full_name, email, department, approval_limit, is_active
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, approvers_data)
        
        # Generate supplier contracts
        cursor.execute("SELECT supplier_id FROM suppliers")
        supplier_rows = cursor.fetchall()
        
        contract_data = []
        for i, (supplier_id,) in enumerate(supplier_rows, 1):
            end_date = date(2025, 12, 31)
            contract_value = round(random.uniform(50000, 500000), 2)
            contract_data.append((
                supplier_id,
                f"CON-2024-{i:03d}",
                "active",
                date(2024, 1, 1),
                end_date,
                contract_value,
                "Net 30",
                1 if random.choice([True, False]) else 0
            ))
        
        batch_insert(conn, """
            INSERT INTO supplier_contracts (
                supplier_id, contract_number, contract_status, start_date, end_date,
                contract_value, payment_terms, auto_renew
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, contract_data)
        
        # Generate company policies
        policy_data = [
            ("Procurement Policy", "procurement", "All purchases over $5,000 require manager approval. Competitive bidding required for orders over $25,000.", "Procurement", 5000, 1),
            ("Order Processing Policy", "order_processing", "Orders processed within 24 hours. Rush orders require $50 fee and manager approval.", "Operations", None, 0),
            ("Budget Authorization", "budget_authorization", "Spending limits: Manager $50K, Director $250K, Executive $1M+", "Finance", None, 1),
            ("Vendor Approval", "vendor_approval", "All new vendors require approval and background check completion.", "Procurement", None, 1)
        ]
        
        batch_insert(conn, """
            INSERT INTO company_policies (
                policy_name, policy_type, policy_content, department, minimum_order_threshold, approval_required
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, policy_data)
        
        # Generate procurement requests
        cursor.execute("SELECT product_id, supplier_id, cost FROM products LIMIT 20")
        product_rows = cursor.fetchall()
        departments = ["Operations", "Finance", "Procurement", "Management"]
        urgency_levels = ["Low", "Normal", "High", "Critical"]
        approval_statuses = ["Pending", "Approved", "Rejected"]
        
        procurement_data = []
        for i in range(25):
            if not product_rows:
                break
            
            product_id, supplier_id, cost = random.choice(product_rows)
            unit_cost = float(cost)
            quantity_requested = random.randint(10, 100)
            total_cost = unit_cost * quantity_requested
            
            request_number = f"PR-2024-{i+1:04d}"
            requester_name = fake.name()
            requester_email = f"{requester_name.lower().replace(' ', '.')}@company.com"
            department = random.choice(departments)
            urgency_level = random.choice(urgency_levels)
            approval_status = random.choices(approval_statuses, weights=[40, 50, 10], k=1)[0]
            
            request_date = date.today() - timedelta(days=random.randint(1, 60))
            required_by_date = request_date + timedelta(days=random.randint(7, 30))
            justification = fake.sentence()
            
            approved_by = None
            approved_at = None
            if approval_status == "Approved":
                approved_by = random.choice([a[0] for a in approvers_data])
                approved_at = request_date + timedelta(days=random.randint(1, 5))
            
            procurement_data.append((
                request_number, requester_name, requester_email, department,
                product_id, supplier_id, quantity_requested, unit_cost, total_cost,
                justification, urgency_level, approval_status, approved_by, approved_at,
                request_date, required_by_date
            ))
        
        if procurement_data:
            batch_insert(conn, """
                INSERT INTO procurement_requests (
                    request_number, requester_name, requester_email, department,
                    product_id, supplier_id, quantity_requested, unit_cost, total_cost,
                    justification, urgency_level, approval_status, approved_by, approved_at,
                    request_date, required_by_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, procurement_data)
        
        # Generate notifications
        cursor.execute("""
            SELECT request_id, requester_email, total_cost, approval_status 
            FROM procurement_requests 
            ORDER BY request_date DESC LIMIT 10
        """)
        recent_requests = cursor.fetchall()
        
        notification_data = []
        for request_id, requester_email, total_cost, approval_status in recent_requests:
            notification_type = "approval_request" if approval_status == "Pending" else "status_update"
            subject = f"Procurement Request {request_id}: {approval_status}"
            message = f"Your procurement request for ${total_cost:.2f} has been {approval_status.lower()}."
            
            notification_data.append((
                request_id,
                notification_type,
                requester_email,
                subject,
                message,
                None
            ))
        
        if notification_data:
            batch_insert(conn, """
                INSERT INTO notifications (
                    request_id, notification_type, recipient_email, subject, message, read_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, notification_data)
        
        logging.info(f"Successfully inserted {len(approvers_data)} approvers!")
        logging.info(f"Successfully inserted {len(contract_data)} supplier contracts!")
        logging.info(f"Successfully inserted {len(policy_data)} company policies!")
        logging.info(f"Successfully inserted {len(procurement_data)} procurement requests!")
        logging.info(f"Successfully inserted {len(notification_data)} notifications!")
        
    except Exception as e:
        logging.error(f"Error inserting agent support data: {e}")
        raise

def insert_orders_and_items(conn, num_orders: int = 50000):
    """Insert order and order item data"""
    try:
        logging.info(f"Generating {num_orders:,} orders and order items...")
        
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id FROM customers ORDER BY RANDOM() LIMIT ?", (num_orders * 2,))
        customer_ids = [row[0] for row in cursor.fetchall()]
        
        if not customer_ids:
            raise Exception("No customers found!")
        
        cursor.execute("SELECT store_id FROM stores")
        store_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT product_id, base_price FROM products")
        product_rows = cursor.fetchall()
        
        orders_data = []
        order_items_data = []
        
        for i in range(num_orders):
            customer_id = random.choice(customer_ids)
            store_id = random.choice(store_ids)
            order_date = date.today() - timedelta(days=random.randint(0, 365))
            
            orders_data.append((customer_id, store_id, order_date))
            
            # Add 1-5 items per order
            num_items = random.randint(1, 5)
            for _ in range(num_items):
                product_id, base_price = random.choice(product_rows)
                quantity = random.randint(1, 10)
                unit_price = base_price
                discount_percent = random.choice([0, 0, 0, 5, 10, 15])
                discount_amount = round((unit_price * quantity * discount_percent) / 100, 2)
                total_amount = round((unit_price * quantity) - discount_amount, 2)
                
                order_items_data.append((
                    i + 1,  # order_id (will be generated)
                    store_id,
                    product_id,
                    quantity,
                    unit_price,
                    discount_percent,
                    discount_amount,
                    total_amount
                ))
        
        # Insert orders first
        batch_insert(conn, 
            "INSERT INTO orders (customer_id, store_id, order_date) VALUES (?, ?, ?)", 
            orders_data)
        
        # Get the actual order IDs that were inserted
        cursor.execute("SELECT order_id FROM orders ORDER BY order_id DESC LIMIT ?", (len(orders_data),))
        order_ids = [row[0] for row in reversed(cursor.fetchall())]
        
        # Update order_items_data with actual order IDs
        updated_order_items = []
        for i, item in enumerate(order_items_data):
            order_idx = min(i // 5, len(order_ids) - 1)  # Distribute items among orders
            updated_order_items.append((
                order_ids[order_idx],
                item[1],
                item[2],
                item[3],
                item[4],
                item[5],
                item[6],
                item[7]
            ))
        
        batch_insert(conn, """
            INSERT INTO order_items (order_id, store_id, product_id, quantity, unit_price, discount_percent, discount_amount, total_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, updated_order_items)
        
        # Insert inventory data (stock levels for products at stores)
        cursor.execute("SELECT store_id FROM stores")
        store_rows = cursor.fetchall()
        cursor.execute("SELECT product_id FROM products")
        product_rows = cursor.fetchall()
        
        inventory_data = []
        for store_id, in store_rows:
            for product_id, in product_rows:
                stock_level = random.randint(0, 1000)
                inventory_data.append((store_id, product_id, stock_level))
        
        batch_insert(conn, 
            "INSERT INTO inventory (store_id, product_id, stock_level) VALUES (?, ?, ?)", 
            inventory_data)
        
        logging.info(f"Successfully inserted {len(orders_data):,} orders!")
        logging.info(f"Successfully inserted {len(order_items_data):,} order items!")
        logging.info(f"Successfully inserted {len(inventory_data):,} inventory records!")
        
    except Exception as e:
        logging.error(f"Error inserting orders: {e}")
        raise

def show_statistics(conn):
    """Display comprehensive database statistics including seasonality analysis"""
    try:
        cursor = conn.cursor()
        
        # Basic table counts
        stats = {
            'stores': cursor.execute("SELECT COUNT(*) FROM stores").fetchone()[0],
            'categories': cursor.execute("SELECT COUNT(*) FROM categories").fetchone()[0],
            'product_types': cursor.execute("SELECT COUNT(*) FROM product_types").fetchone()[0],
            'products': cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0],
            'suppliers': cursor.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0],
            'customers': cursor.execute("SELECT COUNT(*) FROM customers").fetchone()[0],
            'orders': cursor.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            'order_items': cursor.execute("SELECT COUNT(*) FROM order_items").fetchone()[0],
            'inventory': cursor.execute("SELECT COUNT(*) FROM inventory").fetchone()[0],
            'approvers': cursor.execute("SELECT COUNT(*) FROM approvers").fetchone()[0],
            'supplier_contracts': cursor.execute("SELECT COUNT(*) FROM supplier_contracts").fetchone()[0],
            'supplier_performance': cursor.execute("SELECT COUNT(*) FROM supplier_performance").fetchone()[0],
            'company_policies': cursor.execute("SELECT COUNT(*) FROM company_policies").fetchone()[0],
            'procurement_requests': cursor.execute("SELECT COUNT(*) FROM procurement_requests").fetchone()[0],
            'notifications': cursor.execute("SELECT COUNT(*) FROM notifications").fetchone()[0],
        }
        
        logging.info("=" * 70)
        logging.info("📊 DATABASE STATISTICS & ANALYTICS")
        logging.info("=" * 70)
        
        # Table counts
        logging.info("\n📋 TABLE COUNTS:")
        logging.info("-" * 70)
        for table, count in stats.items():
            logging.info(f"  {table:.<45} {count:>15,}")
        
        total_records = sum(stats.values())
        logging.info("-" * 70)
        logging.info(f"  {'TOTAL RECORDS':.<45} {total_records:>15,}")
        
        # Order statistics
        logging.info("\n💰 ORDER STATISTICS:")
        logging.info("-" * 70)
        
        order_stats = cursor.execute("""
            SELECT 
                COUNT(DISTINCT o.order_id) as total_orders,
                ROUND(SUM(oi.total_amount), 2) as total_revenue,
                ROUND(AVG(oi.total_amount), 2) as avg_item_value,
                MIN(oi.total_amount) as min_item,
                MAX(oi.total_amount) as max_item,
                COUNT(DISTINCT o.customer_id) as unique_customers
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
        """).fetchone()
        
        if order_stats[0] > 0:
            total_orders, total_revenue, avg_value, min_order, max_order, unique_custs = order_stats
            logging.info(f"  {'Total Orders':.<45} {total_orders:>15,}")
            logging.info(f"  {'Total Revenue':.<45} ${total_revenue:>14,.2f}")
            logging.info(f"  {'Average Item Value':.<45} ${avg_value:>14,.2f}")
            logging.info(f"  {'Min Item Value':.<45} ${min_order:>14,.2f}")
            logging.info(f"  {'Max Item Value':.<45} ${max_order:>14,.2f}")
            logging.info(f"  {'Unique Customers':.<45} {unique_custs:>15,}")
        
        # Customer statistics
        logging.info("\n👥 CUSTOMER STATISTICS:")
        logging.info("-" * 70)
        
        cust_stats = cursor.execute("""
            SELECT 
                COUNT(*) as total_customers,
                COUNT(DISTINCT primary_store_id) as stores_represented,
                ROUND(COUNT(*) * 1.0 / (SELECT COUNT(*) FROM stores), 1) as avg_per_store
            FROM customers
        """).fetchone()
        
        if cust_stats[0] > 0:
            total_custs, stores_rep, avg_per_store = cust_stats
            logging.info(f"  {'Total Customers':.<45} {total_custs:>15,}")
            logging.info(f"  {'Stores Represented':.<45} {stores_rep:>15,}")
            logging.info(f"  {'Average Per Store':.<45} {avg_per_store:>15,.0f}")
        
        # Top stores by customer count
        logging.info("\n🏪 TOP STORES BY CUSTOMERS:")
        logging.info("-" * 70)
        
        top_stores = cursor.execute("""
            SELECT s.store_name, COUNT(c.customer_id) as customer_count
            FROM stores s
            LEFT JOIN customers c ON s.store_id = c.primary_store_id
            GROUP BY s.store_id
            ORDER BY customer_count DESC
            LIMIT 5
        """).fetchall()
        
        for store_name, count in top_stores:
            pct = (count / stats['customers'] * 100) if stats['customers'] > 0 else 0
            logging.info(f"  {store_name:.<45} {count:>10,} ({pct:>5.1f}%)")
        
        # Product category distribution
        logging.info("\n📦 PRODUCT CATEGORY DISTRIBUTION:")
        logging.info("-" * 70)
        
        categories = cursor.execute("""
            SELECT c.category_name, COUNT(p.product_id) as product_count
            FROM categories c
            LEFT JOIN products p ON c.category_id = p.category_id
            GROUP BY c.category_id
            ORDER BY product_count DESC
        """).fetchall()
        
        for cat_name, count in categories:
            pct = (count / stats['products'] * 100) if stats['products'] > 0 else 0
            logging.info(f"  {cat_name:.<45} {count:>10,} ({pct:>5.1f}%)")
        
        # Supplier performance
        logging.info("\n⭐ SUPPLIER PERFORMANCE METRICS:")
        logging.info("-" * 70)
        
        supplier_metrics = cursor.execute("""
            SELECT 
                ROUND(AVG(s.supplier_rating), 2) as avg_rating,
                COUNT(DISTINCT s.supplier_id) as total_suppliers,
                ROUND(AVG(s.lead_time_days), 1) as avg_lead_time,
                COUNT(DISTINCT sp.performance_id) as total_evaluations
            FROM suppliers s
            LEFT JOIN supplier_performance sp ON s.supplier_id = sp.supplier_id
        """).fetchone()
        
        if supplier_metrics[1] > 0:
            avg_rating, num_suppliers, avg_lead_time, total_evals = supplier_metrics
            logging.info(f"  {'Average Supplier Rating':.<45} {avg_rating:>15.2f}⭐")
            logging.info(f"  {'Total Suppliers':.<45} {num_suppliers:>15,}")
            logging.info(f"  {'Average Lead Time':.<45} {avg_lead_time:>14.1f} days")
            logging.info(f"  {'Performance Evaluations':.<45} {total_evals:>15,}")
        
        # Inventory statistics
        logging.info("\n📊 INVENTORY STATISTICS:")
        logging.info("-" * 70)
        
        inv_stats = cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                ROUND(AVG(stock_level), 1) as avg_stock,
                SUM(stock_level) as total_stock,
                MIN(stock_level) as min_stock,
                MAX(stock_level) as max_stock
            FROM inventory
        """).fetchone()
        
        if inv_stats[0] > 0:
            total_inv, avg_stock, total_stock, min_stock, max_stock = inv_stats
            logging.info(f"  {'Inventory Records':.<45} {total_inv:>15,}")
            logging.info(f"  {'Total Units in Stock':.<45} {total_stock:>15,.0f}")
            logging.info(f"  {'Average Stock per Location':.<45} {avg_stock:>15.1f}")
            logging.info(f"  {'Min Stock Level':.<45} {min_stock:>15,}")
            logging.info(f"  {'Max Stock Level':.<45} {max_stock:>15,}")
        
        # Seasonality analysis
        logging.info("\n🌡️  SEASONALITY ANALYSIS:")
        logging.info("-" * 70)
        
        # Load seasonality data
        seasonal_path = os.path.join(os.path.dirname(__file__), REFERENCE_DATA_DIR, SEASONAL_MULTIPLIERS_FILE)
        try:
            with open(seasonal_path, 'r') as f:
                seasonal_data = json.load(f)
            
            logging.info("\n  Climate Zone Seasonality Factors:")
            for zone, zone_data in seasonal_data['climate_zones'].items():
                logging.info(f"\n  📍 {zone.replace('_', ' ').title()}")
                logging.info(f"     {zone_data['description']}")
                
                for category, multipliers in zone_data['categories'].items():
                    avg_multiplier = sum(multipliers) / len(multipliers)
                    peak_month = max(range(len(multipliers)), key=lambda i: multipliers[i])
                    lowest_month = min(range(len(multipliers)), key=lambda i: multipliers[i])
                    
                    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    peak_name = months[peak_month]
                    low_name = months[lowest_month]
                    
                    peak_val = multipliers[peak_month]
                    low_val = multipliers[lowest_month]
                    
                    logging.info(f"     • {category:.<35} Avg: {avg_multiplier:.2f}x  Peak: {peak_name} ({peak_val:.1f}x)  Low: {low_name} ({low_val:.1f}x)")
        
        except Exception as e:
            logging.info(f"  ⚠️  Could not load seasonality data: {e}")
        
        logging.info("\n" + "=" * 70)
        
    except Exception as e:
        logging.error(f"Error retrieving statistics: {e}")

def main():
    """Main function to orchestrate database generation"""
    try:
        logging.info("Starting SQLite database generation...")
        
        # Create connection
        conn = create_connection()
        
        try:
            # Create schema
            create_database_schema(conn)
            
            # Insert reference data
            insert_stores(conn)
            insert_categories(conn)
            insert_product_types(conn)
            insert_suppliers(conn)
            insert_products(conn)
            
            # Insert transactional data
            insert_customers(conn, num_customers=100000)
            insert_orders_and_items(conn, num_orders=50000)
            
            # Insert agent support data
            insert_agent_support_data(conn)
            
            # Show statistics
            show_statistics(conn)
            
            logging.info("✅ Database generation completed successfully!")
            
        finally:
            conn.close()
            logging.info(f"Connection to {SQLITE_DB_FILE} closed.")
            
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
