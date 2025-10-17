--
-- SQLite Database Schema for Retail System
-- Migrated from PostgreSQL
--

-- Enable foreign keys for SQLite
PRAGMA foreign_keys = ON;

-- ============================================================================
-- Tables
-- ============================================================================

--
-- Name: approvers; Type: TABLE
--

CREATE TABLE approvers (
    approver_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    employee_id TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    department TEXT NOT NULL,
    approval_limit REAL DEFAULT 0.00,
    is_active INTEGER DEFAULT 1
);

--
-- Name: categories; Type: TABLE
--

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    category_name TEXT NOT NULL UNIQUE
);

--
-- Name: company_policies; Type: TABLE
--

CREATE TABLE company_policies (
    policy_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    policy_name TEXT NOT NULL,
    policy_type TEXT NOT NULL CHECK (policy_type IN ('procurement', 'order_processing', 'budget_authorization', 'vendor_approval')),
    policy_content TEXT NOT NULL,
    department TEXT,
    minimum_order_threshold REAL,
    approval_required INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1
);

--
-- Name: customers; Type: TABLE
--

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    primary_store_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (primary_store_id) REFERENCES stores(store_id)
);

--
-- Name: inventory; Type: TABLE
--

CREATE TABLE inventory (
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    stock_level INTEGER NOT NULL,
    PRIMARY KEY (store_id, product_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

--
-- Name: notifications; Type: TABLE
--

CREATE TABLE notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    request_id INTEGER,
    notification_type TEXT NOT NULL CHECK (notification_type IN ('approval_request', 'status_update', 'completion')),
    recipient_email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    read_at DATETIME,
    FOREIGN KEY (request_id) REFERENCES procurement_requests(request_id)
);

--
-- Name: order_items; Type: TABLE
--

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    order_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    discount_percent INTEGER DEFAULT 0,
    discount_amount REAL DEFAULT 0,
    total_amount REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);

--
-- Name: orders; Type: TABLE
--

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    customer_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);

--
-- Name: procurement_requests; Type: TABLE
--

CREATE TABLE procurement_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    request_number TEXT NOT NULL UNIQUE,
    requester_name TEXT NOT NULL,
    requester_email TEXT NOT NULL,
    department TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    quantity_requested INTEGER NOT NULL,
    unit_cost REAL NOT NULL,
    total_cost REAL NOT NULL,
    justification TEXT,
    urgency_level TEXT DEFAULT 'Normal' CHECK (urgency_level IN ('Low', 'Normal', 'High', 'Critical')),
    approval_status TEXT DEFAULT 'Pending' CHECK (approval_status IN ('Pending', 'Approved', 'Rejected', 'On Hold')),
    approved_by TEXT,
    approved_at DATETIME,
    request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    required_by_date DATE,
    vendor_restrictions TEXT,
    esg_requirements INTEGER DEFAULT 0,
    bulk_discount_eligible INTEGER DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

--
-- Name: product_description_embeddings; Type: TABLE
--

CREATE TABLE product_description_embeddings (
    product_id INTEGER PRIMARY KEY NOT NULL,
    description_embedding TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

--
-- Name: product_image_embeddings; Type: TABLE
--

CREATE TABLE product_image_embeddings (
    product_id INTEGER NOT NULL,
    image_url TEXT NOT NULL,
    image_embedding TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id, image_url),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

--
-- Name: product_types; Type: TABLE
--

CREATE TABLE product_types (
    type_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    category_id INTEGER NOT NULL,
    type_name TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

--
-- Name: products; Type: TABLE
--

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    cost REAL NOT NULL,
    base_price REAL NOT NULL,
    gross_margin_percent REAL DEFAULT 33.00,
    product_description TEXT NOT NULL,
    procurement_lead_time_days INTEGER DEFAULT 14,
    minimum_order_quantity INTEGER DEFAULT 1,
    discontinued INTEGER DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (type_id) REFERENCES product_types(type_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

--
-- Name: stores; Type: TABLE
--

CREATE TABLE stores (
    store_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    store_name TEXT NOT NULL UNIQUE,
    rls_user_id TEXT NOT NULL,
    is_online INTEGER DEFAULT 0 NOT NULL
);

--
-- Name: supplier_contracts; Type: TABLE
--

CREATE TABLE supplier_contracts (
    contract_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    supplier_id INTEGER NOT NULL,
    contract_number TEXT NOT NULL UNIQUE,
    contract_status TEXT DEFAULT 'active' CHECK (contract_status IN ('active', 'expired', 'terminated')),
    start_date DATE NOT NULL,
    end_date DATE,
    contract_value REAL,
    payment_terms TEXT NOT NULL,
    auto_renew INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

--
-- Name: supplier_performance; Type: TABLE
--

CREATE TABLE supplier_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    supplier_id INTEGER NOT NULL,
    evaluation_date DATE NOT NULL,
    cost_score REAL DEFAULT 3.00 CHECK (cost_score >= 0 AND cost_score <= 5),
    quality_score REAL DEFAULT 3.00 CHECK (quality_score >= 0 AND quality_score <= 5),
    delivery_score REAL DEFAULT 3.00 CHECK (delivery_score >= 0 AND delivery_score <= 5),
    compliance_score REAL DEFAULT 3.00 CHECK (compliance_score >= 0 AND compliance_score <= 5),
    overall_score REAL DEFAULT 3.00 CHECK (overall_score >= 0 AND overall_score <= 5),
    notes TEXT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

--
-- Name: suppliers; Type: TABLE
--

CREATE TABLE suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    supplier_name TEXT NOT NULL,
    supplier_code TEXT NOT NULL UNIQUE,
    contact_email TEXT,
    contact_phone TEXT,
    address_line1 TEXT,
    address_line2 TEXT,
    city TEXT,
    state_province TEXT,
    postal_code TEXT,
    country TEXT DEFAULT 'USA',
    payment_terms TEXT DEFAULT 'Net 30',
    lead_time_days INTEGER DEFAULT 14,
    minimum_order_amount REAL DEFAULT 0.00,
    bulk_discount_threshold REAL DEFAULT 10000.00,
    bulk_discount_percent REAL DEFAULT 5.00,
    supplier_rating REAL DEFAULT 3.00 CHECK (supplier_rating >= 0 AND supplier_rating <= 5),
    esg_compliant INTEGER DEFAULT 1,
    approved_vendor INTEGER DEFAULT 1,
    preferred_vendor INTEGER DEFAULT 0,
    active_status INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Indexes
-- ============================================================================

CREATE INDEX idx_approvers_department ON approvers(department);
CREATE INDEX idx_approvers_limit ON approvers(approval_limit);
CREATE INDEX idx_categories_name ON categories(category_name);
CREATE INDEX idx_company_policies_threshold ON company_policies(minimum_order_threshold);
CREATE INDEX idx_company_policies_type ON company_policies(policy_type);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_primary_store ON customers(primary_store_id);
CREATE INDEX idx_inventory_product ON inventory(product_id);
CREATE INDEX idx_inventory_store ON inventory(store_id);
CREATE INDEX idx_inventory_store_product ON inventory(store_id, product_id);
CREATE INDEX idx_notifications_request ON notifications(request_id);
CREATE INDEX idx_notifications_type ON notifications(notification_type);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_order_items_store ON order_items(store_id);
CREATE INDEX idx_order_items_total ON order_items(total_amount);
CREATE INDEX idx_order_items_covering ON order_items(order_id, store_id, product_id, total_amount, quantity);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_store ON orders(store_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
CREATE INDEX idx_orders_store_date ON orders(store_id, order_date);
CREATE INDEX idx_procurement_requests_date ON procurement_requests(request_date);
CREATE INDEX idx_procurement_requests_department ON procurement_requests(department);
CREATE INDEX idx_procurement_requests_number ON procurement_requests(request_number);
CREATE INDEX idx_procurement_requests_product ON procurement_requests(product_id);
CREATE INDEX idx_procurement_requests_requester ON procurement_requests(requester_email);
CREATE INDEX idx_procurement_requests_status ON procurement_requests(approval_status);
CREATE INDEX idx_procurement_requests_supplier ON procurement_requests(supplier_id);
CREATE INDEX idx_procurement_requests_urgency ON procurement_requests(urgency_level);
CREATE INDEX idx_product_image_embeddings_product ON product_image_embeddings(product_id);
CREATE INDEX idx_product_image_embeddings_url ON product_image_embeddings(image_url);
CREATE INDEX idx_product_types_category ON product_types(category_id);
CREATE INDEX idx_product_types_name ON product_types(type_name);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_cost ON products(cost);
CREATE INDEX idx_products_discontinued ON products(discontinued);
CREATE INDEX idx_products_lead_time ON products(procurement_lead_time_days);
CREATE INDEX idx_products_margin ON products(gross_margin_percent);
CREATE INDEX idx_products_price ON products(base_price);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_products_type ON products(type_id);
CREATE INDEX idx_products_covering ON products(category_id, type_id, product_id, sku, cost, base_price);
CREATE INDEX idx_products_sku_covering ON products(sku, product_id, product_name, cost, base_price);
CREATE INDEX idx_stores_name ON stores(store_name);
CREATE INDEX idx_supplier_contracts_status ON supplier_contracts(contract_status);
CREATE INDEX idx_supplier_contracts_supplier ON supplier_contracts(supplier_id);
CREATE INDEX idx_supplier_performance_date ON supplier_performance(evaluation_date);
CREATE INDEX idx_supplier_performance_overall ON supplier_performance(overall_score);
CREATE INDEX idx_supplier_performance_supplier ON supplier_performance(supplier_id);
CREATE INDEX idx_suppliers_active ON suppliers(active_status);
CREATE INDEX idx_suppliers_approved ON suppliers(approved_vendor);
CREATE INDEX idx_suppliers_code ON suppliers(supplier_code);
CREATE INDEX idx_suppliers_esg ON suppliers(esg_compliant);
CREATE INDEX idx_suppliers_name ON suppliers(supplier_name);
CREATE INDEX idx_suppliers_preferred ON suppliers(preferred_vendor);
CREATE INDEX idx_suppliers_rating ON suppliers(supplier_rating);

-- ============================================================================
-- Views
-- ============================================================================

--
-- Name: vw_company_supplier_policies
--

CREATE VIEW vw_company_supplier_policies AS
SELECT 
    policy_id,
    policy_name,
    policy_type,
    policy_content,
    department,
    minimum_order_threshold,
    approval_required,
    is_active,
    CASE
        WHEN policy_type = 'procurement' THEN 'Covers supplier selection and procurement processes'
        WHEN policy_type = 'vendor_approval' THEN 'Defines vendor approval and onboarding requirements'
        WHEN policy_type = 'budget_authorization' THEN 'Specifies budget limits and authorization levels'
        WHEN policy_type = 'order_processing' THEN 'Outlines order processing and fulfillment procedures'
        ELSE 'General company policy'
    END AS policy_description,
    LENGTH(policy_content) AS content_length
FROM company_policies
WHERE is_active = 1;

--
-- Name: vw_supplier_contract_details
--

CREATE VIEW vw_supplier_contract_details AS
SELECT 
    s.supplier_id,
    s.supplier_name,
    s.supplier_code,
    s.contact_email,
    s.contact_phone,
    sc.contract_id,
    sc.contract_number,
    sc.contract_status,
    sc.start_date,
    sc.end_date,
    sc.contract_value,
    sc.payment_terms,
    sc.auto_renew,
    sc.created_at AS contract_created,
    CASE
        WHEN sc.end_date IS NOT NULL THEN CAST((julianday(sc.end_date) - julianday(DATE('now'))) AS INTEGER)
        ELSE NULL
    END AS days_until_expiry,
    CASE
        WHEN sc.end_date IS NOT NULL AND sc.end_date <= DATE('now', '+90 days') THEN 1
        ELSE 0
    END AS renewal_due_soon
FROM suppliers s
LEFT JOIN supplier_contracts sc ON s.supplier_id = sc.supplier_id
WHERE sc.contract_status = 'active' OR sc.contract_status IS NULL;

--
-- Name: vw_supplier_history_performance
--

CREATE VIEW vw_supplier_history_performance AS
SELECT 
    s.supplier_id,
    s.supplier_name,
    s.supplier_code,
    s.supplier_rating,
    s.esg_compliant,
    s.preferred_vendor,
    s.lead_time_days,
    s.created_at AS supplier_since,
    sp.evaluation_date,
    sp.cost_score,
    sp.quality_score,
    sp.delivery_score,
    sp.compliance_score,
    sp.overall_score,
    sp.notes AS performance_notes,
    COUNT(pr.request_id) AS total_requests,
    COALESCE(SUM(pr.total_cost), 0) AS total_value
FROM suppliers s
LEFT JOIN supplier_performance sp ON s.supplier_id = sp.supplier_id
LEFT JOIN procurement_requests pr ON s.supplier_id = pr.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.supplier_code, s.supplier_rating, s.esg_compliant, 
         s.preferred_vendor, s.lead_time_days, s.created_at, sp.evaluation_date, sp.cost_score,
         sp.quality_score, sp.delivery_score, sp.compliance_score, sp.overall_score, sp.notes;

--
-- Name: vw_suppliers_for_request
--

CREATE VIEW vw_suppliers_for_request AS
SELECT DISTINCT
    s.supplier_id,
    s.supplier_name,
    s.supplier_code,
    s.contact_email,
    s.contact_phone,
    s.supplier_rating,
    s.esg_compliant,
    s.preferred_vendor,
    s.approved_vendor,
    s.lead_time_days,
    s.minimum_order_amount,
    s.bulk_discount_threshold,
    s.bulk_discount_percent,
    s.payment_terms,
    COUNT(DISTINCT p.product_id) AS available_products,
    COALESCE(AVG(sp.overall_score), s.supplier_rating) AS avg_performance_score,
    sc.contract_status,
    sc.contract_number,
    c.category_name
FROM suppliers s
LEFT JOIN products p ON s.supplier_id = p.supplier_id
LEFT JOIN categories c ON p.category_id = c.category_id
LEFT JOIN supplier_performance sp ON s.supplier_id = sp.supplier_id 
    AND sp.evaluation_date >= DATE('now', '-6 months')
LEFT JOIN supplier_contracts sc ON s.supplier_id = sc.supplier_id 
    AND sc.contract_status = 'active'
WHERE s.active_status = 1 AND s.approved_vendor = 1
GROUP BY s.supplier_id, s.supplier_name, s.supplier_code, s.contact_email, s.contact_phone, 
         s.supplier_rating, s.esg_compliant, s.preferred_vendor, s.approved_vendor, 
         s.lead_time_days, s.minimum_order_amount, s.bulk_discount_threshold, 
         s.bulk_discount_percent, s.payment_terms, sc.contract_status, sc.contract_number, 
         c.category_name;
