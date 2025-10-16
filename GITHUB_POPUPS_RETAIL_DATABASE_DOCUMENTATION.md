# GitHub Popup Stores Retail Database Documentation

## Overview
This document provides comprehensive documentation for the GitHub Popup retail database schema, including product catalog, inventory management, supplier information, and database structure across 16 store locations.

**Generated:** October 15, 2025 (Updated)  
**Database:** PostgreSQL - GitHub Popup Retail System  
**Schema:** retail

**Key Features:**
- **Static Supplier Data**: All supplier contracts, codes, and values are managed through JSON reference files for consistent database generation
- **Predictable Contract Values**: All 20 supplier contracts use static values rounded to $10K with standardized numbering and realistic end dates
- **Reproducible Database**: Static reference data ensures identical results across multiple database generations for reliable testing and development

---

## Table of Contents
1. [Products by Category and Type](#products-by-category-and-type)
2. [Popup Store Inventory Status](#popup-store-inventory-status)
3. [Supplier Information](#supplier-information)
4. [Company Policies](#company-policies)
5. [MCP Servers](#mcp-servers)
6. [Complete Database Schema](#complete-database-schema)

---

## Products by Category and Type

### Product Catalog Summary

| Category | Product Type | Total Products | Products Available |
|----------|-------------|----------------|-------------------|
| **Accessories** | Backpacks & Bags | 9 | Canvas Tote Bag, Classic School Backpack, Crossbody Sling Bag, Hiking Daypack, Laptop Commuter Backpack, Mini Fashion Backpack, Rolling Travel Backpack, Sports Gym Backpack, Waterproof Dry Bag |
| | Belts | 4 | Braided Leather Belt, Canvas Web Belt, Leather Dress Belt, Reversible Belt |
| | Caps & Hats | 8 | Baseball Cap Classic, Beanie Winter Hat, Bucket Hat, Fedora Hat, Fleece Ear Warmer Headband, Knit Pom Beanie, Snapback Hat, Trucker Cap Mesh |
| | Gloves | 4 | Fleece Liner Gloves, Touchscreen Gloves, Waterproof Winter Gloves, Winter Knit Gloves |
| | Scarves | 4 | Cashmere Blend Scarf, Fleece Neck Gaiter, Infinity Loop Scarf, Plaid Winter Scarf |
| | Socks | 8 | Athletic Crew Socks Pack, Casual Cotton Socks, Compression Athletic Socks, Cozy Slipper Socks, Dress Socks Set, No-Show Ankle Socks, Thermal Winter Socks, Wool Hiking Socks |
| | Sunglasses | 4 | Classic Aviator Sunglasses, Round Frame Sunglasses, Sport Wrap Sunglasses, Wayfarer Sunglasses |
| **Apparel - Bottoms** | Jeans | 9 | Bootcut Denim Jeans, Classic Straight Leg Jeans, Dark Wash Jeans, Distressed Fashion Jeans, High-Waist Mom Jeans, Raw Selvedge Jeans, Relaxed Fit Comfort Jeans, Skinny Fit Jeans, Slim Fit Stretch Jeans |
| | Pants | 4 | Cargo Pants Utility, Chino Pants, Corduroy Pants, Jogger Sweatpants |
| | Shorts | 4 | Athletic Running Shorts, Cargo Shorts, Casual Chino Shorts, Denim Shorts |
| **Apparel - Tops** | Flannel Shirts | 4 | Classic Plaid Flannel, Flannel Shirt Jacket, Heavyweight Work Flannel, Slim Fit Flannel Shirt |
| | Formal Shirts | 8 | Chambray Work Shirt, Classic White Dress Shirt, Flannel Button-Down, French Cuff Dress Shirt, Oxford Button-Down Shirt, Slim Fit Dress Shirt, Striped Business Shirt, Wrinkle-Free Business Shirt |
| | Hoodies | 7 | Athletic Performance Hoodie, Logo Print Hoodie, Oversized Comfort Hoodie, Pullover Fleece Hoodie, Sherpa Lined Hoodie, Tech Fleece Hoodie, Zip-Up Hoodie Jacket |
| | Sweatshirts | 4 | Crewneck Sweatshirt, Mock Neck Sweatshirt, Quarter-Zip Pullover, Vintage College Sweatshirt |
| | T-Shirts | 12 | Athletic Performance Tee, Classic Cotton T-Shirt, Graphic Print T-Shirt, Henley Long Sleeve Tee, Long Sleeve Basic Tee, Pocket T-Shirt, Polo Style T-Shirt, Raglan Baseball Tee, Scoop Neck Tee, Striped Casual T-Shirt, Thermal Waffle Tee, V-Neck Casual Tee |
| **Footwear** | Boots | 5 | Chelsea Ankle Boots, Combat Boots, Rain Boots Waterproof, Waterproof Hiking Boots, Work Boots Steel Toe |
| | Dress Shoes | 5 | Brogue Wingtip Shoes, Derby Dress Shoes, Loafer Slip-On Shoes, Monk Strap Shoes, Oxford Leather Shoes |
| | Sandals | 3 | Flip Flops, Slide Sandals, Sport Sandals |
| | Sneakers | 9 | Classic White Sneakers, High-Top Sneakers, Mesh Athletic Sneakers, Platform Sneakers, Retro Style Sneakers, Running Athletic Shoes, Skate Shoes, Slip-On Canvas Sneakers, Trail Running Shoes |
| **Outerwear** | Coats | 4 | Parka Winter Coat, Peacoat Wool Blend, Rain Coat Long, Trench Coat |
| | Jackets | 10 | Bomber Jacket, Denim Jacket Classic, Down Parka, Fleece Zip Jacket, Leather Jacket, Puffer Jacket, Quilted Vest, Rain Jacket Waterproof, Softshell Jacket, Windbreaker Sport Jacket |

**Total Product Categories:** 5  
**Total Product Types:** 21  
**Total Unique Products:** 129

---

## GitHub Popup Store Inventory Status

### Inventory Summary by Store

| Store Name | Unique Products | Total Items | Total Inventory Value (Retail) |
|------------|----------------|-------------|------------------------------|
| **Physical Popup Stores** |
| GitHub Popup Atlanta Midtown | 42 | 347 | $24,855.89 |
| GitHub Popup Austin Downtown | 50 | 434 | $26,639.52 |
| GitHub Popup Boston Back Bay | 45 | 354 | $23,280.00 |
| GitHub Popup Chicago Loop | 47 | 386 | $26,144.93 |
| GitHub Popup Denver LoDo | 52 | 433 | $30,455.71 |
| GitHub Popup Miami Design District | 41 | 288 | $17,989.75 |
| GitHub Popup Minneapolis Mill District | 50 | 421 | $31,414.38 |
| GitHub Popup Nashville Music Row | 44 | 376 | $25,649.49 |
| GitHub Popup NYC Times Square | 52 | 519 | $33,804.13 |
| GitHub Popup Phoenix Scottsdale | 42 | 346 | $23,184.30 |
| GitHub Popup Portland Pearl District | 42 | 344 | $28,992.90 |
| GitHub Popup Raleigh Research Triangle | 44 | 401 | $31,207.56 |
| GitHub Popup Salt Lake City Downtown | 50 | 411 | $32,906.88 |
| GitHub Popup Seattle Capitol Hill | 45 | 423 | $32,955.78 |
| GitHub Popup SF Union Square | 47 | 417 | $34,034.09 |
| **Online Store** |
| GitHub Popup Online Store | 129 | 6,217 | $437,821.29 |

**Total Popup Stores:** 16 (15 Physical + 1 Online)  
**Total Physical Store Inventory Value:** $423,515.31  
**Total Online Store Inventory Value:** $437,821.29  
**Total Combined Inventory Value:** $861,336.60  
**Average Physical Store Inventory Value:** $28,234.35

### Store Distribution & Themes

**Geographic Coverage:** 15 major US cities + online presence

| Store Location | Theme | Climate Zone | Product Strategy |
|---------------|--------|--------------|-----------------|
| NYC Times Square | Urban Tech Hub | Temperate | Curated Selection |
| SF Union Square | West Coast Tech | Warm | Curated Selection |
| Austin Downtown | Creative Tech | Warm | Curated Selection |
| Denver LoDo | Mountain Tech | Temperate | Curated Selection |
| Chicago Loop | Midwest Professional | Temperate | Curated Selection |
| Boston Back Bay | Academic Tech | Temperate | Curated Selection |
| Seattle Capitol Hill | Grunge Tech Revival | Pacific Northwest | Curated Selection |
| Atlanta Midtown | Southern Tech Hub | Warm | Curated Selection |
| Miami Design District | Tropical Tech Style | Warm | Curated Selection |
| Portland Pearl District | Eco-Tech Portland | Pacific Northwest | Curated Selection |
| Nashville Music Row | Music City Tech | Temperate | Curated Selection |
| Phoenix Scottsdale | Desert Tech Oasis | Warm | Curated Selection |
| Minneapolis Mill District | Northern Tech Heritage | Temperate | Curated Selection |
| Raleigh Research Triangle | Research Park Professional | Temperate | Curated Selection |
| Salt Lake City Downtown | Mountain West Tech | Temperate | Curated Selection |
| **Online Store** | Global Developer Community | All Zones | Complete Catalog |

### Product Distribution Strategy
- **Physical Stores:** Each store carries 40-55 curated products (~30% average of total catalog)
- **Online Store:** Complete product catalog (129 products)
- **Product Overlap:** ~20-30% core essentials shared across stores
- **Unique Assortment:** 70-80% store-specific products based on local themes and demographics

---

## Supplier Information

### Supplier Directory

| Supplier Name | Code | Location | Contact | ESG Compliant | Approved | Preferred | Rating |
|--------------|------|----------|---------|---------------|----------|-----------|--------|
| **Active Wear Solutions** | SUP010 | Tacoma, WA | amanda@activewear.com | ✅ Yes | ✅ Yes | ⭐ Yes | 4.80 |
| **Athletic Footwear Network** | SUP016 | Everett, WA | ryan.clark@athleticfootwear.com | ✅ Yes | ✅ Yes | ⭐ Yes | 2.00 |
| **Bag & Luggage Distributors** | SUP013 | Spokane, WA | daniel.white@bagluggage.com | ✅ Yes | ✅ Yes | ⭐ Yes | 4.70 |
| **Classic Outerwear Imports** | SUP011 | Seattle, WA | thomas.brown@classicouterwear.com | ❌ No | ✅ Yes | ❌ No | 4.40 |
| **Comfort Footwear Wholesale** | SUP007 | Everett, WA | robert@comfortfootwear.com | ✅ Yes | ✅ Yes | ⭐ Yes | 4.70 |
| **Elite Fashion Distributors** | SUP002 | Bellevue, WA | sarah.j@elitefashion.com | ✅ Yes | ✅ Yes | ⭐ Yes | 4.90 |
| **Fashion Forward Wholesale** | SUP014 | Redmond, WA | michelle@fashionforward.com | ✅ Yes | ✅ Yes | ⭐ Yes | 4.80 |
| **Footwear Direct International** | SUP006 | Redmond, WA | lisa.t@footweardirect.com | ✅ Yes | ✅ Yes | ⭐ Yes | 4.20 |
| **Formal Wear Specialists** | SUP017 | Seattle, WA | susan.moore@formalwear.com | ✅ Yes | ✅ Yes | ⭐ Yes | 3.70 |
| **Global Headwear Co** | SUP009 | Kirkland, WA | chris.w@globalheadwear.com | ❌ No | ✅ Yes | ❌ No | 2.00 |
| **Metro Style Supply Co** | SUP004 | Seattle, WA | e.rodriguez@metrostyle.com | ✅ Yes | ✅ Yes | ⭐ Yes | 2.50 |
| **Northwest Denim Works** | SUP005 | Spokane, WA | david.kim@nwdenim.com | ✅ Yes | ✅ Yes | ⭐ Yes | 4.80 |
| **Pacific Apparel Group** | SUP003 | Tacoma, WA | james@pacificapparel.com | ✅ Yes | ✅ Yes | ⭐ Yes | 4.70 |
| **Premier Accessories Ltd** | SUP008 | Seattle, WA | j.lee@premieraccessories.com | ✅ Yes | ✅ Yes | ⭐ Yes | 2.80 |
| **Premium Denim Source** | SUP015 | Tacoma, WA | kevin@premiumdenim.com | ❌ No | ✅ Yes | ❌ No | 3.60 |
| **Quality Basics Wholesale** | SUP020 | Tacoma, WA | mark.j@qualitybasics.com | ✅ Yes | ✅ Yes | ⭐ Yes | 4.80 |
| **Sock & Hosiery Wholesale** | SUP012 | Bellevue, WA | patricia@socksupply.com | ✅ Yes | ✅ Yes | ⭐ Yes | 4.90 |
| **Streetwear Collective** | SUP018 | Kirkland, WA | jason@streetwearcollective.com | ✅ Yes | ✅ Yes | ⭐ Yes | 4.70 |
| **Urban Threads Wholesale** | SUP001 | Seattle, WA | michael.chen@urbanthreads.com | ✅ Yes | ✅ Yes | ⭐ Yes | 3.50 |
| **Winter Wear Supply Co** | SUP019 | Spokane, WA | karen@winterwear.com | ❌ No | ✅ Yes | ❌ No | 3.50 |

#### 💰 Supplier Bulk Discount Programs

All GitHub Popup suppliers offer bulk discount programs with varying thresholds and discount rates. **Note**: Discounts apply automatically when order values exceed the specified thresholds.

**Best Discount Rates:**
- **Northwest Denim Works (SUP005)**: 9.49% discount on orders $4,000+
- **Comfort Footwear Wholesale (SUP007)**: 9.26% discount on orders $3,000+
- **Footwear Direct International (SUP006)**: 9.25% discount on orders $7,500+
- **Formal Wear Specialists (SUP017)**: 9.07% discount on orders $10,000+
- **Quality Basics Wholesale (SUP020)**: 8.99% discount on orders $2,500+

**Most Accessible Discounts (Lowest Thresholds):**
- **Sock & Hosiery Wholesale (SUP012)**: 7.28% discount on orders $1,500+
- **Premier Accessories Ltd (SUP008)**: 7.92% discount on orders $2,000+
- **Quality Basics Wholesale (SUP020)**: 8.99% discount on orders $2,500+
- **Urban Threads Wholesale (SUP001)**: 6.46% discount on orders $2,500+
- **Global Headwear Co (SUP009)**: 5.98% discount on orders $2,500+

**Premium Volume Discounts (High Thresholds):**
- **Classic Outerwear Imports (SUP011)**: 7.44% discount on orders $12,500+
- **Formal Wear Specialists (SUP017)**: 9.07% discount on orders $10,000+
- **Metro Style Supply Co (SUP004)**: 8.86% discount on orders $10,000+

**💡 Procurement Tip**: Quality Basics Wholesale offers the best combination of high discount rate (8.99%) and accessible threshold ($2,500), making them ideal for regular orders. Northwest Denim Works provides the highest discount rate at 9.49% for denim needs, while Sock & Hosiery Wholesale offers the lowest threshold at $1,500 for smaller frequent orders.

### Supplier Key Metrics

- **Total Suppliers:** 20
- **ESG Compliant:** 16 (80%)
- **Approved Vendors:** 20 (100%)
- **Preferred Vendors:** 16 (80%)
- **Average Rating:** 4.00/5.0
- **Geographic Coverage:** Washington State
- **Contract Management:** All supplier contracts use static data from JSON reference files for consistent database generation

### Static Supplier Data Implementation

**📋 Controlled Contract Data:**
All supplier contract information is now managed through static JSON data for consistent, predictable database generation:

- **Contract Values:** Static values ranging from $80K to $600K, all rounded to nearest $10,000
- **Contract Numbers:** Standardized format `2024-XXXX-NNN` with unique 4-letter codes per supplier
- **Contract End Dates:** Systematic distribution between 1-2 years from current date
- **Supplier Codes:** Sequential format `SUP001` through `SUP020` for easy identification
- **Supplier IDs:** Sequential integers 1-20 matching database primary keys

**Benefits:**
- **Reproducible Results:** Identical database content across multiple generations
- **Testing Reliability:** Predictable data for consistent testing scenarios  
- **Contract Realism:** Realistic contract values and terms based on supplier size and category
- **Data Integrity:** All supplier-related fields controlled via single JSON source

### Payment Terms Distribution
- **Net 30:** 11 suppliers (55%)
- **Net 45:** 6 suppliers (30%)
- **Net 60:** 3 suppliers (15%)

### Lead Time Analysis
- **Average Lead Time:** 14.3 days
- **Fastest Delivery:** 5 days (Sock & Hosiery Wholesale)
- **Longest Lead Time:** 28 days (Classic Outerwear Imports)

---

## Company Policies

### Active Company Policies

| Policy Name | Type | Department | Min Order Threshold | Approval Required |
|-------------|------|------------|-------------------|------------------|
| **Budget Authorization** | Budget Authorization | Finance | - | ✅ Required |
| **Order Processing Policy** | Order Processing | Operations | - | ❌ Not Required |
| **Procurement Policy** | Procurement | Procurement | $5,000.00 | ✅ Required |
| **Vendor Approval** | Vendor Approval | Procurement | - | ✅ Required |

### Policy Details

#### Budget Authorization Policy (Finance)
- **Content:** Spending limits: Manager $50K, Director $250K, Executive $1M+
- **Approval:** Required for all transactions

#### Procurement Policy (Procurement)
- **Content:** All purchases over $5,000 require manager approval. Competitive bidding required for orders over $25,000.
- **Minimum Threshold:** $5,000.00
- **Approval:** Required above threshold

#### Order Processing Policy (Operations)
- **Content:** Orders processed within 24 hours. Rush orders require $50 fee and manager approval.
- **Approval:** Not required for standard orders

#### Vendor Approval Policy (Procurement)
- **Content:** All new vendors require approval and background check completion.
- **Approval:** Required for all new vendors

---

## MCP Servers

The Zava Retail system includes three specialized Model Context Protocol (MCP) servers that provide AI agents with access to different aspects of the retail database and operations. Each server runs on a dedicated port and offers specific tools for different business functions.

### 🏦 Finance Agent MCP Server (Port 8002)

**Purpose:** Provides finance-related tools and operations to support finance agents with order policies, contracts, sales analysis, and inventory management.

**Endpoint:** `http://localhost:8002/mcp`

#### Available Tools:

##### 1. `get_company_order_policy`
**Purpose:** Retrieves company order processing policies and budget authorization rules.

**Input Parameters:**
- `department` (Optional[str]): Optional department name to filter policies (e.g., "Procurement", "Finance")

**Returns:** JSON string with format `{"c": [columns], "r": [[row data]], "n": count}` containing policy names, types, content, thresholds, and approval requirements.

##### 2. `get_supplier_contract`
**Purpose:** Gets supplier contract information including terms and conditions.

**Input Parameters:**
- `supplier_id` (int): The unique identifier for the supplier (required)

**Returns:** JSON string with format `{"c": [columns], "r": [[row data]], "n": count}` containing contract details, dates, values, and calculated expiry information.

##### 3. `get_historical_sales_data`
**Purpose:** Retrieves historical sales data with revenue, order counts, and customer metrics.

**Input Parameters:**
- `days_back` (int): Number of days to look back (default: 90)
- `store_id` (Optional[int]): Optional store ID to filter results
- `category_name` (Optional[str]): Optional category name to filter results

**Returns:** JSON string with format `{"c": [columns], "r": [[row data]], "n": count}` containing date, store, category, revenue, orders, and customer metrics.

##### 4. `get_current_inventory_status`
**Purpose:** Gets current inventory status across stores with values and low stock alerts.

**Input Parameters:**
- `store_id` (Optional[int]): Optional store ID to filter results
- `category_name` (Optional[str]): Optional category name to filter results
- `low_stock_threshold` (int): Stock level below which to trigger alert (default: 50)

**Returns:** JSON string with format `{"c": [columns], "r": [[row data]], "n": count}` containing store, product, category, stock levels, values, and alerts.

##### 5. `get_current_utc_date`
**Purpose:** Gets the current date and time in UTC format for date calculations and time-sensitive operations.

**Input Parameters:** None

**Returns:** ISO 8601 formatted UTC datetime string (YYYY-MM-DDTHH:MM:SS.ffffffZ)

---

### 📊 Sales Analysis MCP Server (Port 8000)

**Purpose:** Provides comprehensive customer sales database access with individual table schema tools and semantic search capabilities for Zava Retail business operations.

**Endpoint:** `http://localhost:8000/mcp`

#### Available Tools:

##### 1. `semantic_search_products`
**Purpose:** Searches for Zava products using natural language descriptions to find matches based on semantic similarity.

**Input Parameters:**
- `query_description` (str): Describe the Zava product you're looking for using natural language. Include purpose, features, or use case.
- `max_rows` (int): The maximum number of products to return (default: 20)
- `similarity_threshold` (float): A value between 20 and 80 that sets the minimum similarity threshold (default: 30.0)

**Returns:** JSON with compact success format `{"c":["col1","col2"],"r":[[v11,v12],[v21,v22]],"n":2}` or error format with "err" field.

##### 2. `get_multiple_table_schemas`
**Purpose:** Retrieves schemas for multiple database tables to understand data structure.

**Input Parameters:**
- `table_names` (list[str]): List of table names from the retail schema (customers, stores, categories, products, orders, etc.)

**Returns:** Concatenated schema strings for the requested tables.

##### 3. `execute_sales_query`
**Purpose:** Executes PostgreSQL queries against the sales database with proper validation and formatting.

**Input Parameters:**
- `postgresql_query` (str): A well-formed PostgreSQL query

**Returns:** Query results as a formatted string with proper column headers and data.

##### 4. `get_current_utc_date`
**Purpose:** Gets the current UTC date and time for time-sensitive analysis.

**Input Parameters:** None

**Returns:** Current UTC date and time in ISO format (YYYY-MM-DDTHH:MM:SS.fffffZ)

---

### 🏭 Supplier Agent MCP Server (Port 8001)

**Purpose:** Provides tools to support supplier management operations including supplier discovery, performance analysis, contract management, and policy compliance.

**Endpoint:** `http://localhost:8001/mcp`

#### Available Tools:

##### 1. `find_suppliers_for_request`
**Purpose:** Finds suppliers that match procurement request requirements based on various criteria.

**Input Parameters:**
- `product_category` (Optional[str]): Product category to filter suppliers by (e.g., 'Tools', 'Hardware', 'Building Materials')
- `esg_required` (bool): Whether ESG compliance is required (default: false)
- `min_rating` (float): Minimum supplier rating required 0.0 to 5.0 (default: 3.0)
- `max_lead_time` (int): Maximum acceptable lead time in days (default: 30)
- `budget_min` (Optional[float]): Minimum budget amount to consider suppliers
- `budget_max` (Optional[float]): Maximum budget amount to filter suppliers
- `limit` (int): Maximum number of suppliers to return (default: 10)

**Returns:** JSON with supplier details including ratings, contact info, terms, and contract status.

##### 2. `get_supplier_history_and_performance`
**Purpose:** Gets detailed supplier performance history and metrics for evaluation.

**Input Parameters:**
- `supplier_id` (int): Unique identifier of the supplier
- `months_back` (int): Number of months of history to retrieve (default: 12)

**Returns:** JSON with performance scores, evaluation dates, procurement history, and trend data.

##### 3. `get_supplier_contract`
**Purpose:** Gets supplier contract details and terms for a specific supplier.

**Input Parameters:**
- `supplier_id` (int): Unique identifier of the supplier

**Returns:** JSON with contract details, terms, values, dates, and renewal status.

##### 4. `get_company_supplier_policy`
**Purpose:** Gets company policies related to supplier management and procurement processes.

**Input Parameters:**
- `policy_type` (Optional[str]): Type of policy ('procurement', 'vendor_approval', 'budget_authorization', 'order_processing')
- `department` (Optional[str]): Department-specific policies to retrieve

**Returns:** JSON with policy documents, procedures, requirements, and approval thresholds.

##### 5. `get_current_utc_date`
**Purpose:** Gets the current UTC date and time for time-sensitive supplier analysis.

**Input Parameters:** None

**Returns:** Current UTC date and time in ISO format (YYYY-MM-DDTHH:MM:SS.fffffZ)

---

### MCP Server Configuration

**Server Architecture:**
- All servers use FastMCP framework for HTTP-based communication
- Each server maintains its own database connection pool
- Azure Application Insights integration for telemetry (optional)
- Row Level Security (RLS) support with user context headers

**Security Features:**
- Request context validation with `x-rls-user-id` header
- Database connection pooling for performance
- Comprehensive error handling and logging
- Structured JSON responses with consistent format

**Usage Pattern:**
1. **Finance Agent** → Finance MCP Server (8002) for financial data and policies
2. **Sales Agent** → Sales Analysis MCP Server (8000) for product search and sales queries  
3. **Supplier Agent** → Supplier MCP Server (8001) for vendor management and procurement

---

## Seasonality and Climate Zone System

### Climate Zone Classification

The GitHub Popup retail system implements sophisticated seasonal demand patterns based on three climate zones:

#### 🌲 Pacific Northwest Zone
**Description:** Washington, Oregon, Northern California - mild, wet winters and dry summers  
**Stores:** Seattle Capitol Hill, Portland Pearl District

**Seasonal Multipliers by Category (Jan-Dec):**
- **Outerwear:** [1.8, 1.7, 1.5, 1.3, 1.0, 0.7, 0.6, 0.6, 0.9, 1.3, 1.6, 1.8] - High winter demand
- **Apparel - Tops:** [0.7, 0.7, 0.8, 0.9, 1.1, 1.3, 1.4, 1.3, 1.1, 0.9, 0.7, 0.6] - Summer peak
- **Footwear:** [0.9, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.3, 1.2, 1.1, 0.9, 0.8] - Spring/summer preference
- **Accessories:** [1.2, 1.2, 1.1, 1.0, 1.0, 1.1, 1.2, 1.2, 1.1, 1.0, 1.1, 1.3] - Winter accessories demand
- - **Apparel - Bottoms:** [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] - Stable year-round

#### 🌡️ Temperate Zone  
**Description:** Most US regions - moderate seasonal variation  
**Stores:** NYC Times Square, Denver LoDo, Chicago Loop, Boston Back Bay, Nashville Music Row, Minneapolis Mill District, Raleigh Research Triangle, Salt Lake City Downtown

**Seasonal Multipliers by Category (Jan-Dec):**
- **Outerwear:** [1.6, 1.6, 1.4, 1.1, 0.8, 0.6, 0.5, 0.6, 0.8, 1.0, 1.3, 1.6] - Strong winter pattern
- **Apparel - Tops:** [0.8, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.2, 1.1, 1.0, 0.8, 0.7] - Summer focused
- **Footwear:** [0.9, 0.9, 1.0, 1.1, 1.1, 1.2, 1.2, 1.2, 1.1, 1.0, 0.9, 0.9] - Moderate variation
- **Accessories:** [1.2, 1.2, 1.1, 1.0, 1.0, 0.9, 0.8, 0.9, 1.0, 1.0, 1.1, 1.2] - Winter accessory preference
- **Apparel - Bottoms:** [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] - Stable year-round

#### ☀️ Warm Zone
**Description:** Southern US regions - milder winters, hot summers  
**Stores:** SF Union Square, Austin Downtown, Atlanta Midtown, Miami Design District, Phoenix Scottsdale

**Seasonal Multipliers by Category (Jan-Dec):**
- **Outerwear:** [1.3, 1.3, 1.2, 1.0, 0.7, 0.5, 0.4, 0.5, 0.7, 0.9, 1.1, 1.3] - Mild winter demand
- **Apparel - Tops:** [0.9, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.3, 1.2, 1.1, 0.9, 0.8] - Strong summer demand
- **Footwear:** [1.0, 1.0, 1.1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.2, 1.1, 1.0, 1.0] - Summer footwear preference
- **Accessories:** [1.1, 1.1, 1.0, 1.0, 0.9, 0.8, 0.7, 0.8, 0.9, 1.0, 1.1, 1.1] - Lower summer demand
- **Apparel - Bottoms:** [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] - Stable year-round

### Seasonal Business Intelligence



### Seasonal Business Intelligence

**Key Insights:**
- **Outerwear** shows the strongest seasonal variation across all zones (0.4x to 1.8x multipliers)
- **Apparel - Bottoms** (jeans, pants, shorts) maintain stable demand year-round in all climates
- **Pacific Northwest** has the most extreme seasonal patterns due to distinct wet/dry seasons
- **Warm zones** show inverted patterns - higher summer demand for most categories except outerwear
- **Q4 (Oct-Dec)** is universally strong for outerwear and accessories across all zones

**Procurement Strategy:**
- Stock outerwear heavily in Q3 for Q4/Q1 demand, especially in temperate and Pacific Northwest zones
- Summer apparel (tops, footwear) should peak in Q2 inventory for Q2/Q3 sales
- Warm zone stores need different inventory timing compared to northern stores

---

## Complete Database Schema

### Row Level Security (RLS) Implementation

The GitHub Popup retail database implements PostgreSQL Row Level Security to ensure data isolation between stores:

**RLS User System:**
- Each store has a unique `rls_user_id` (UUID) that controls data access
- **Super Manager UUID:** `00000000-0000-0000-0000-000000000000` - Has access to all data across stores
- Store-specific UUIDs restrict access to relevant data only

**Key RLS Tables:**
- `retail.stores` - Each store has unique rls_user_id for access control
- `retail.customers` - Customer data tied to primary store via foreign key
- `retail.orders` - Order access controlled by store association
- `retail.inventory` - Inventory visible only to authorized store users

**Security Benefits:**
- Multi-tenant architecture within single database
- Store managers only see their store's data
- Corporate users (with super manager UUID) have full access
- Prevents accidental data exposure between stores

### Core Tables Overview

The GitHub Popup retail database consists of 17 tables organized into the following functional areas:

1. **Customer Management**: `customers`
2. **Store Management**: `stores` (with RLS user mapping)
3. **Product Catalog**: `categories`, `product_types`, `products`
4. **Order Management**: `orders`, `order_items`
5. **Inventory Management**: `inventory`
6. **Supplier Management**: `suppliers`, `supplier_performance`, `supplier_contracts`
7. **Procurement**: `procurement_requests`, `company_policies`, `approvers`, `notifications`
8. **AI/ML Features**: `product_image_embeddings`, `product_description_embeddings`

**Recent Schema Enhancements:**
- **Enhanced Store Model**: Added `is_online` boolean field to distinguish physical vs online stores
- **RLS Integration**: All stores now have `rls_user_id` for row-level security
- **Comprehensive Supplier Data**: Full supplier contracts and performance tracking
- **Bulk Discount System**: Supplier-specific discount thresholds and percentages
- **Climate Zone Support**: Seasonal multipliers integrated with geographic store data

---

### Table Schemas

---

## Database Summary & Key Metrics

### Current Database State (October 2025)
- **Total Stores:** 16 (15 Physical Popup Stores + 1 Online Store)
- **Geographic Coverage:** 15 major US cities with themed popup locations
- **Total Products:** 129 unique products across 5 categories and 21 product types
- **Active Suppliers:** 20 suppliers across Washington State
- **ESG Compliance:** 80% of suppliers are ESG compliant
- **Inventory Value:** $861,336.60 total retail value ($424K physical + $438K online)
- **Climate Zones:** 3-zone seasonal system (Pacific Northwest, Temperate, Warm)

### Data Architecture Highlights
- **Row Level Security (RLS):** Multi-tenant database with store-level data isolation
- **Vector Embeddings:** AI-powered product search via pgvector extension  
- **Seasonal Intelligence:** Climate zone-based demand forecasting
- **Supplier Integration:** Comprehensive procurement workflow with bulk discounts
- **Real-time Inventory:** Live stock levels across all store locations

### Use Cases & Applications
- **Store Operations:** Individual store inventory management and sales tracking
- **Corporate Analytics:** Cross-store performance analysis and trend identification
- **Procurement Optimization:** Supplier selection, bulk discount utilization, ESG compliance
- **Seasonal Planning:** Climate-aware inventory planning and seasonal product mix
- **Customer Intelligence:** Purchase pattern analysis and store preference insights
- **AI-Powered Search:** Semantic product discovery using vector embeddings

---

## Table Schemas

#### 1. retail.customers
**Purpose:** Customer information and store associations

| Column | Type | Description |
|--------|------|-------------|
| customer_id | integer | Primary key, unique customer identifier |
| first_name | text | Customer's first name |
| last_name | text | Customer's last name |
| email | text | Customer's email address |
| phone | text | Customer's phone number |
| primary_store_id | integer | Foreign key to retail.stores |
| created_at | timestamp | Account creation timestamp |

**Relationships:**
- `primary_store_id` → `retail.stores.store_id` (MANY_TO_ONE)

---

#### 2. retail.stores
**Purpose:** Store locations and configuration

| Column | Type | Description |
|--------|------|-------------|
| store_id | integer | Primary key, unique store identifier |
| store_name | text | Store display name |
| rls_user_id | uuid | Row-level security user identifier |
| is_online | boolean | True for online store, false for popup |

**Valid Store Locations:**
- GitHub Popup Online Store
- GitHub Popup Atlanta Midtown
- GitHub Popup Austin Downtown
- GitHub Popup Boston Back Bay
- GitHub Popup Chicago Loop
- GitHub Popup Denver LoDo
- GitHub Popup Miami Design District
- GitHub Popup Minneapolis Mill District
- GitHub Popup Nashville Music Row
- GitHub Popup NYC Times Square
- GitHub Popup Phoenix Scottsdale
- GitHub Popup Portland Pearl District
- GitHub Popup Raleigh Research Triangle
- GitHub Popup Salt Lake City Downtown
- GitHub Popup Seattle Capitol Hill
- GitHub Popup SF Union Square

---

#### 3. retail.categories
**Purpose:** Product category definitions

| Column | Type | Description |
|--------|------|-------------|
| category_id | integer | Primary key, unique category identifier |
| category_name | text | Category display name |

**Valid Categories:**
- Accessories
- Apparel - Bottoms
- Apparel - Tops
- Footwear
- Outerwear

---

#### 4. retail.product_types
**Purpose:** Product type definitions within categories

| Column | Type | Description |
|--------|------|-------------|
| type_id | integer | Primary key, unique type identifier |
| category_id | integer | Foreign key to retail.categories |
| type_name | text | Product type display name |

**Relationships:**
- `category_id` → `retail.categories.category_id` (MANY_TO_ONE)

**Valid Product Types:** 21 types across 5 categories (see Product Catalog section)

---

#### 5. retail.products
**Purpose:** Complete product catalog with pricing and sourcing

| Column | Type | Description |
|--------|------|-------------|
| product_id | integer | Primary key, unique product identifier |
| sku | text | Stock keeping unit code |
| product_name | text | Product display name |
| category_id | integer | Foreign key to retail.categories |
| type_id | integer | Foreign key to retail.product_types |
| supplier_id | integer | Foreign key to retail.suppliers |
| cost | numeric | Product cost from supplier |
| base_price | numeric | Retail selling price |
| gross_margin_percent | numeric | Calculated profit margin |
| product_description | text | Detailed product description |
| procurement_lead_time_days | integer | Days to receive from supplier |
| minimum_order_quantity | integer | Minimum order quantity from supplier |
| discontinued | boolean | Product availability status |

**Relationships:**
- `category_id` → `retail.categories.category_id` (MANY_TO_ONE)
- `supplier_id` → `retail.suppliers.supplier_id` (ONE_TO_MANY)
- `type_id` → `retail.product_types.type_id` (MANY_TO_ONE)

---

#### 6. retail.orders
**Purpose:** Order header information

| Column | Type | Description |
|--------|------|-------------|
| order_id | integer | Primary key, unique order identifier |
| customer_id | integer | Foreign key to retail.customers |
| store_id | integer | Foreign key to retail.stores |
| order_date | date | Order placement date |

**Relationships:**
- `customer_id` → `retail.customers.customer_id` (MANY_TO_ONE)
- `store_id` → `retail.stores.store_id` (MANY_TO_ONE)

**Available Data Years:** 2020-2026

---

#### 7. retail.order_items
**Purpose:** Individual line items within orders

| Column | Type | Description |
|--------|------|-------------|
| order_item_id | integer | Primary key, unique line item identifier |
| order_id | integer | Foreign key to retail.orders |
| store_id | integer | Foreign key to retail.stores |
| product_id | integer | Foreign key to retail.products |
| quantity | integer | Quantity ordered |
| unit_price | numeric | Price per unit at time of sale |
| discount_percent | integer | Percentage discount applied |
| discount_amount | numeric | Dollar amount discount |
| total_amount | numeric | Final line item total |

**Relationships:**
- `product_id` → `retail.products.product_id` (MANY_TO_ONE)
- `store_id` → `retail.stores.store_id` (MANY_TO_ONE)
- `order_id` → `retail.orders.order_id` (MANY_TO_ONE)

---

#### 8. retail.inventory
**Purpose:** Current stock levels by store and product

| Column | Type | Description |
|--------|------|-------------|
| store_id | integer | Foreign key to retail.stores (composite key) |
| product_id | integer | Foreign key to retail.products (composite key) |
| stock_level | integer | Current quantity in stock |

**Relationships:**
- `product_id` → `retail.products.product_id` (MANY_TO_ONE)
- `store_id` → `retail.stores.store_id` (MANY_TO_ONE)

---

#### 9. retail.suppliers
**Purpose:** Supplier master data and business terms

| Column | Type | Description |
|--------|------|-------------|
| supplier_id | integer | Primary key, unique supplier identifier |
| supplier_name | text | Supplier company name |
| supplier_code | text | Internal supplier code |
| contact_email | text | Primary contact email |
| contact_phone | text | Primary contact phone |
| address_line1 | text | Street address |
| address_line2 | text | Additional address info |
| city | text | City |
| state_province | text | State or province |
| postal_code | text | Zip or postal code |
| country | text | Country |
| payment_terms | text | Payment terms (Net 30, Net 45, etc.) |
| lead_time_days | integer | Standard delivery lead time |
| minimum_order_amount | numeric | Minimum order value required |
| bulk_discount_threshold | numeric | Order value for bulk discount |
| bulk_discount_percent | numeric | Bulk discount percentage |
| supplier_rating | numeric | Overall supplier performance rating |
| esg_compliant | boolean | ESG compliance status |
| approved_vendor | boolean | Vendor approval status |
| preferred_vendor | boolean | Preferred vendor status |
| active_status | boolean | Active supplier status |
| created_at | timestamp | Record creation date |
| last_updated | timestamp | Last update timestamp |

---

#### 10. retail.supplier_performance
**Purpose:** Historical supplier performance evaluations

| Column | Type | Description |
|--------|------|-------------|
| performance_id | integer | Primary key, unique evaluation identifier |
| supplier_id | integer | Foreign key to retail.suppliers |
| evaluation_date | date | Date of performance evaluation |
| cost_score | numeric | Cost competitiveness score |
| quality_score | numeric | Product quality score |
| delivery_score | numeric | On-time delivery score |
| compliance_score | numeric | Regulatory compliance score |
| overall_score | numeric | Calculated overall score |
| notes | text | Evaluation notes and comments |

**Relationships:**
- `supplier_id` → `retail.suppliers.supplier_id` (ONE_TO_MANY)

---

#### 11. retail.procurement_requests
**Purpose:** Purchase requisitions and approval workflow

| Column | Type | Description |
|--------|------|-------------|
| request_id | integer | Primary key, unique request identifier |
| request_number | text | Human-readable request number |
| requester_name | text | Name of person making request |
| requester_email | text | Requester's email address |
| department | text | Requesting department |
| product_id | integer | Foreign key to retail.products |
| supplier_id | integer | Foreign key to retail.suppliers |
| quantity_requested | integer | Quantity being requested |
| unit_cost | numeric | Expected unit cost |
| total_cost | numeric | Total request value |
| justification | text | Business justification for purchase |
| urgency_level | text | Priority level (Low, Medium, High, Critical) |
| approval_status | text | Current approval status |
| approved_by | text | Name of approver |
| approved_at | timestamp | Approval timestamp |
| request_date | timestamp | Request creation date |
| required_by_date | date | Date product is needed |
| vendor_restrictions | text | Any vendor restrictions |
| esg_requirements | boolean | ESG compliance required |
| bulk_discount_eligible | boolean | Eligible for bulk discounts |

**Relationships:**
- `product_id` → `retail.products.product_id` (MANY_TO_ONE)
- `supplier_id` → `retail.suppliers.supplier_id` (ONE_TO_MANY)

---

#### 12. retail.company_policies
**Purpose:** Company procurement and approval policies

| Column | Type | Description |
|--------|------|-------------|
| policy_id | integer | Primary key, unique policy identifier |
| policy_name | text | Policy display name |
| policy_type | text | Policy category |
| policy_content | text | Full policy text |
| department | text | Applicable department |
| minimum_order_threshold | numeric | Minimum order value for policy |
| approval_required | boolean | Whether approval is required |
| is_active | boolean | Policy active status |

---

#### 13. retail.supplier_contracts
**Purpose:** Supplier contract management

| Column | Type | Description |
|--------|------|-------------|
| contract_id | integer | Primary key, unique contract identifier |
| supplier_id | integer | Foreign key to retail.suppliers |
| contract_number | text | Contract reference number |
| contract_status | text | Contract status |
| start_date | date | Contract effective date |
| end_date | date | Contract expiration date |
| contract_value | numeric | Total contract value |
| payment_terms | text | Payment terms |
| auto_renew | boolean | Automatic renewal flag |
| created_at | timestamp | Contract creation date |

**Relationships:**
- `supplier_id` → `retail.suppliers.supplier_id` (ONE_TO_MANY)

---

#### 14. retail.approvers
**Purpose:** Approval authority and limits

| Column | Type | Description |
|--------|------|-------------|
| approver_id | integer | Primary key, unique approver identifier |
| employee_id | text | Employee identifier |
| full_name | text | Approver's full name |
| email | text | Approver's email address |
| department | text | Approver's department |
| approval_limit | numeric | Maximum approval amount |
| is_active | boolean | Active approver status |

---

#### 15. retail.notifications
**Purpose:** System notifications and communications

| Column | Type | Description |
|--------|------|-------------|
| notification_id | integer | Primary key, unique notification identifier |
| request_id | integer | Foreign key to retail.procurement_requests |
| notification_type | text | Type of notification |
| recipient_email | text | Notification recipient |
| subject | text | Notification subject line |
| message | text | Notification message body |
| sent_at | timestamp | Notification send time |
| read_at | timestamp | Notification read time |

**Relationships:**
- `request_id` → `retail.procurement_requests.request_id` (ONE_TO_MANY)

---

#### 16. retail.product_image_embeddings
**Purpose:** AI-powered image search capabilities

| Column | Type | Description |
|--------|------|-------------|
| product_id | integer | Foreign key to retail.products |
| image_url | text | Product image URL |
| image_embedding | vector | AI-generated image embedding |
| created_at | timestamp | Embedding creation date |

**Relationships:**
- `product_id` → `retail.products.product_id` (MANY_TO_ONE)

---

#### 17. retail.product_description_embeddings
**Purpose:** AI-powered semantic product search

| Column | Type | Description |
|--------|------|-------------|
| product_id | integer | Foreign key to retail.products |
| description_embedding | vector | AI-generated text embedding |
| created_at | timestamp | Embedding creation date |

**Relationships:**
- `product_id` → `retail.products.product_id` (MANY_TO_ONE)

---

## Seasonal Variations and Trends

### Sales Performance by Season (2024 Data)

#### Revenue by Category and Season

| Season | Accessories | Apparel - Bottoms | Apparel - Tops | Footwear | Outerwear | **Total** |
|--------|-------------|-------------------|----------------|----------|-----------|-----------|
| **Winter** | $239,850 | $316,606 | $196,265 | $427,114 | $952,882 | **$2,132,717** |
| **Spring** | $204,702 | $324,351 | $235,231 | $542,415 | $750,553 | **$2,057,252** |
| **Summer** | $228,692 | $320,793 | $316,074 | $604,621 | $434,389 | **$1,904,569** |
| **Fall** | $210,562 | $325,715 | $243,169 | $544,030 | $708,398 | **$2,031,874** |

#### Seasonal Trends Analysis

**Winter (Dec-Feb)**: Peak Season
- **Highest Revenue**: $2.13M (26.3% of annual sales)
- **Top Category**: Outerwear dominates with $952K revenue
- **Key Drivers**: Coats, jackets, and winter accessories
- **Average Order Value**: Highest due to expensive outerwear items

**Spring (Mar-May)**: Transition Period
- **Revenue**: $2.06M (25.4% of annual sales)
- **Balanced Growth**: Even distribution across categories
- **Top Category**: Footwear leads with $542K
- **Trend**: Customers refresh wardrobes after winter

**Summer (Jun-Aug)**: Lowest Revenue Period
- **Revenue**: $1.90M (23.5% of annual sales)
- **Top Category**: Footwear peaks at $605K (sandals, sneakers)
- **Notable**: Apparel-Tops increases (T-shirts, lighter clothing)
- **Pattern**: Outerwear drops to lowest levels ($434K)

**Fall (Sep-Nov)**: Preparation Season
- **Revenue**: $2.03M (25.1% of annual sales)
- **Trend**: Building toward winter, outerwear sales increase
- **Top Category**: Footwear remains strong at $544K
- **Pattern**: Steady preparation for colder months

### Product Type Seasonal Popularity

#### Winter Best Sellers
1. **Jackets** - 3,108 units sold, $611K revenue
2. **Jeans** - 1,490 units sold, $199K revenue
3. **Coats** - 1,285 units sold, $342K revenue
4. **Sneakers** - 1,030 units sold, $159K revenue
5. **T-Shirts** - 795 units sold, $41K revenue

#### Summer Best Sellers
1. **Jeans** - 1,447 units sold, $195K revenue
2. **Sneakers** - 1,445 units sold, $221K revenue
3. **Jackets** - 1,351 units sold, $258K revenue (lighter varieties)
4. **T-Shirts** - 1,253 units sold, $62K revenue
5. **Formal Shirts** - 871 units sold, $97K revenue

### Inventory Management by Seasonal Category

#### Current Stock Distribution

| Seasonal Category | Product Types | Total Stock | Avg Stock/Product | Inventory Value |
|------------------|---------------|-------------|------------------|-----------------|
| **Winter-Focused** | 7 types | 1,032 units | 10.5 | $95,097 |
| **Summer-Focused** | 4 types | 587 units | 10.1 | $25,758 |
| **Year-Round** | 4 types | 1,045 units | 10.6 | $82,197 |
| **Seasonal-Flexible** | 6 types | 849 units | 9.7 | $44,404 |

#### Seasonal Stocking Strategies

**Winter-Focused Items** (38% of inventory value):
- **Jackets**: Highest stock levels (398 units, $43K value)
- **Hoodies**: Moderate stock (177 units, $11K value)  
- **Boots**: Premium items (159 units, $22K value)
- **Coats**: Lower volume, high value (75 units, $11K value)

**Summer-Focused Items** (10% of inventory value):
- **T-Shirts**: High volume, lower value (278 units, $8K value)
- **Shorts**: Moderate stock (143 units, $7K value)
- **Sunglasses**: Premium accessories (116 units, $8K value)
- **Sandals**: Seasonal footwear (50 units, $3K value)

**Year-Round Essentials** (33% of inventory value):
- **Sneakers**: Consistent demand (269 units, $26K value)
- **Jeans**: Stable throughout year (286 units, $24K value)
- **Backpacks & Bags**: Steady sales (280 units, $17K value)
- **Formal Shirts**: Business wear (210 units, $14K value)

### Seasonal Business Insights

#### Peak Shopping Periods
1. **January**: Post-holiday sales, winter gear demand
2. **March**: Spring wardrobe refresh
3. **July**: Summer peak for footwear and casual wear
4. **October**: Back-to-school and winter preparation

#### Inventory Recommendations
- **Pre-Winter (Sep-Nov)**: Increase outerwear stock by 40-50%
- **Pre-Summer (Apr-Jun)**: Focus on footwear and casual wear
- **Post-Holiday (Jan-Feb)**: Maintain winter stock, prepare spring transition
- **Mid-Summer (Jul-Aug)**: Emphasize T-shirts, shorts, and sandals

#### Revenue Optimization Opportunities
- **Winter Premium**: Leverage high-value outerwear for maximum revenue
- **Summer Volume**: Focus on quantity sales of casual items
- **Year-Round Stability**: Maintain consistent stock of essentials
- **Seasonal Transitions**: Plan inventory shifts 6-8 weeks in advance

---

## Key Features

### 1. Multi-Store Support
- Online store and 7 popup locations
- Store-specific inventory management
- Row-level security for multi-tenant access

### 2. Comprehensive Product Catalog
- **5 major categories with 21 product types
- 129 unique products
- Full supplier integration with cost and pricing

### 3. Advanced Supplier Management
- ESG compliance tracking
- Performance monitoring and rating system
- Contract and procurement workflow management

### 4. AI-Powered Search
- Image-based product search via embeddings
- Semantic text search for natural language queries
- Enhanced product discovery capabilities

### 5. Robust Approval Workflow
- Multi-level approval processes
- Department-specific policies
- Automated notification system

### 6. Seasonal Intelligence
- Comprehensive seasonal sales analysis
- Category-specific seasonal patterns
- Inventory optimization by seasonal demand
- Revenue forecasting based on historical trends

