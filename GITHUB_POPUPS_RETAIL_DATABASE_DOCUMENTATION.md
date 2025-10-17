# GitHub Popup Stores Retail Database Documentation

## Overview
This document provides comprehensive documentation for the GitHub Popup retail database schema, including product catalog, inventory management, supplier information, and database structure across 16 store locations.

**Generated:** October 17, 2025 (Updated)  
**Database:** SQLite - GitHub Popup Retail System  
**Database File:** `data/retail.db`  
**Data Models:** `app/models/sqlite/` directory

**Key Features:**
- **Lightweight Database**: File-based SQLite database for easy deployment and portability
- **Static Supplier Data**: All supplier contracts, codes, and values are managed through JSON reference files for consistent database generation
- **Predictable Contract Values**: All 20 supplier contracts use static values rounded to $10K with standardized numbering and realistic end dates
- **Reproducible Database**: Static reference data ensures identical results across multiple database generations for reliable testing and development
- **Diverse Supplier Network**: 20 suppliers with varied ratings (3.2-4.8), ESG compliance (55%), and performance tiers for realistic procurement scenarios

**Supplier Data Quality:**
The database contains realistic, diverse supplier data sourced from `data/database/reference_data/supplier_data.json`:
- **Varied Ratings:** From 3.2 (Global Headwear) to 4.8 (Urban Threads) for realistic vendor comparisons
- **ESG Diversity:** 11 ESG-compliant suppliers (55%) and 9 non-compliant for filtering scenarios
- **Approval Status:** 17 approved vendors, 3 pending review (Global Headwear, Streetwear Collective, Quality Basics)
- **Preferred Vendors:** 4 top-tier suppliers marked as preferred for priority procurement
- **Lead Time Variation:** 9-25 day range for testing time-sensitive procurement decisions
- **Payment Terms:** Mix of Net 30 (70%), Net 45 (20%), and Net 60 (10%) for diverse cash flow scenarios
- **Real Contact Information:** Authentic email addresses and supplier names for workshop demonstrations

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
| GitHub Popup Atlanta Midtown | 30 | 307 | $10,514.93 |
| GitHub Popup Austin Downtown | 30 | 260 | $9,395.40 |
| GitHub Popup Boston Back Bay | 30 | 312 | $15,145.88 |
| GitHub Popup Chicago Loop | 30 | 306 | $14,433.94 |
| GitHub Popup Denver LoDo | 30 | 288 | $14,935.12 |
| GitHub Popup Miami Design District | 30 | 331 | $15,667.69 |
| GitHub Popup Minneapolis Mill District | 30 | 300 | $13,693.00 |
| GitHub Popup Nashville Music Row | 30 | 354 | $16,088.46 |
| GitHub Popup NYC Times Square | 30 | 326 | $14,987.74 |
| GitHub Popup Phoenix Scottsdale | 30 | 331 | $14,686.69 |
| GitHub Popup Portland Pearl District | 30 | 284 | $14,409.16 |
| GitHub Popup Raleigh Research Triangle | 30 | 337 | $17,270.63 |
| GitHub Popup Salt Lake City Downtown | 30 | 360 | $16,609.40 |
| GitHub Popup Seattle Capitol Hill | 30 | 312 | $14,559.88 |
| GitHub Popup SF Union Square | 30 | 288 | $11,837.12 |
| **Online Store** |
| GitHub Popup Online Store | 30 | 318 | $19,618.82 |

**Total Popup Stores:** 16 (15 Physical + 1 Online)  
**Total Physical Store Inventory Value:** $214,235.04  
**Total Online Store Inventory Value:** $19,618.82  
**Total Combined Inventory Value:** $233,853.86  
**Average Physical Store Inventory Value:** $14,282.34

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
- **Physical Stores:** Each store carries exactly 30 curated products (~23% of total catalog)
- **Online Store:** Carries 30 products (same selection as physical stores)
- **Product Overlap:** All stores carry the same 30 core products
- **Unique Assortment:** Consistent product selection across all locations

---

## Supplier Information

### Supplier Directory

| Supplier Name | Code | Location | Contact | ESG Compliant | Approved | Preferred | Rating | Lead Time |
|--------------|------|----------|---------|---------------|----------|-----------|--------|-----------|
| **Urban Threads Wholesale** | SUP001 | Seattle, WA | michael.chen@urbanthreads.com | ✅ Yes | ✅ Yes | ⭐ **Yes** | 4.80 | 10 days |
| **Elite Fashion Distributors** | SUP002 | Seattle, WA | sarah.j@elitefashion.com | ✅ Yes | ✅ Yes | ⭐ **Yes** | 4.50 | 12 days |
| **Pacific Apparel Group** | SUP003 | Seattle, WA | james@pacificapparel.com | ✅ Yes | ✅ Yes | ❌ No | 3.80 | 14 days |
| **Metro Style Supply Co** | SUP004 | Seattle, WA | e.rodriguez@metrostyle.com | ❌ No | ✅ Yes | ❌ No | 4.20 | 18 days |
| **Northwest Denim Works** | SUP005 | Seattle, WA | david.kim@nwdenim.com | ✅ Yes | ✅ Yes | ❌ No | 3.90 | 15 days |
| **Footwear Direct International** | SUP006 | Seattle, WA | lisa.t@footweardirect.com | ✅ Yes | ✅ Yes | ⭐ **Yes** | 4.60 | 11 days |
| **Comfort Footwear Wholesale** | SUP007 | Seattle, WA | robert@comfortfootwear.com | ❌ No | ✅ Yes | ❌ No | 4.10 | 16 days |
| **Premier Accessories Ltd** | SUP008 | Seattle, WA | j.lee@premieraccessories.com | ❌ No | ✅ Yes | ❌ No | 3.50 | 20 days |
| **Global Headwear Co** | SUP009 | Seattle, WA | chris.w@globalheadwear.com | ❌ No | ⚠️ **No** | ❌ No | 3.20 | 25 days |
| **Active Wear Solutions** | SUP010 | Seattle, WA | amanda@activewear.com | ✅ Yes | ✅ Yes | ❌ No | 4.30 | 13 days |
| **Classic Outerwear Imports** | SUP011 | Seattle, WA | thomas.brown@classicouterwear.com | ✅ Yes | ✅ Yes | ❌ No | 4.40 | 14 days |
| **Sock & Hosiery Wholesale** | SUP012 | Seattle, WA | patricia@socksupply.com | ❌ No | ✅ Yes | ❌ No | 3.60 | 17 days |
| **Bag & Luggage Distributors** | SUP013 | Seattle, WA | daniel.white@bagluggage.com | ✅ Yes | ✅ Yes | ❌ No | 4.00 | 15 days |
| **Fashion Forward Wholesale** | SUP014 | Seattle, WA | michelle@fashionforward.com | ✅ Yes | ✅ Yes | ⭐ **Yes** | 4.70 | 9 days |
| **Premium Denim Source** | SUP015 | Seattle, WA | kevin@premiumdenim.com | ❌ No | ✅ Yes | ❌ No | 3.70 | 19 days |
| **Athletic Footwear Network** | SUP016 | Seattle, WA | ryan.clark@athleticfootwear.com | ✅ Yes | ✅ Yes | ❌ No | 4.20 | 14 days |
| **Formal Wear Specialists** | SUP017 | Seattle, WA | susan.moore@formalwear.com | ❌ No | ✅ Yes | ❌ No | 3.90 | 18 days |
| **Streetwear Collective** | SUP018 | Seattle, WA | jason@streetwearcollective.com | ❌ No | ⚠️ **No** | ❌ No | 3.40 | 22 days |
| **Winter Wear Supply Co** | SUP019 | Seattle, WA | karen@winterwear.com | ✅ Yes | ✅ Yes | ❌ No | 4.00 | 16 days |
| **Quality Basics Wholesale** | SUP020 | Seattle, WA | mark.j@qualitybasics.com | ❌ No | ⚠️ **No** | ❌ No | 3.30 | 24 days |

#### 💰 Supplier Bulk Discount Programs

All GitHub Popup suppliers offer bulk discount programs with varying discount rates. **Note**: Discounts apply automatically when order values exceed $2,500.

**Discount Rates by Supplier:**
- **Supplier 17 (SUP017)**: 9.47% discount on orders $2,500+
- **Supplier 11 (SUP011)**: 8.90% discount on orders $2,500+
- **Supplier 2 (SUP002)**: 8.74% discount on orders $2,500+
- **Supplier 3 (SUP003)**: 8.41% discount on orders $2,500+
- **Supplier 1 (SUP001)**: 8.38% discount on orders $2,500+

**All Suppliers:**
All 20 suppliers offer consistent terms:
- **Bulk Discount Threshold**: $2,500 minimum order
- **Discount Rates**: Range from 5.12% to 9.47%
- **Payment Terms**: Net 30 (all suppliers)
- **Lead Time**: 14 days (all suppliers)

**💡 Procurement Tip**: All suppliers have the same minimum order threshold ($2,500) and payment terms (Net 30). Choose suppliers based on their discount rate, with Supplier 17 offering the best rate at 9.47%.

### Supplier Key Metrics

- **Total Suppliers:** 20
- **ESG Compliant:** 11 (55%) - ✅ Majority ESG certified
- **Approved Vendors:** 17 (85%) - ⚠️ 3 suppliers pending approval
- **Preferred Vendors:** 4 (20%) - ⭐ Top-tier partners
- **Average Rating:** 4.01/5.0 (Range: 3.2 to 4.8)
- **Lead Time Range:** 9-25 days (Average: 16.2 days)
- **Geographic Coverage:** All suppliers located in Seattle, WA
- **Contract Management:** All supplier contracts use static data from JSON reference files for consistent database generation

**Supplier Tiers:**
- **🌟 Premium Tier (Rating ≥ 4.5):** 4 suppliers - Urban Threads (4.8), Fashion Forward (4.7), Footwear Direct (4.6), Elite Fashion (4.5)
- **⭐ High Performance (Rating 4.0-4.4):** 7 suppliers - Classic Outerwear, Active Wear, Metro Style, Athletic Footwear, Comfort Footwear, Bag & Luggage, Winter Wear
- **✓ Standard Tier (Rating 3.5-3.9):** 6 suppliers - Northwest Denim, Formal Wear, Pacific Apparel, Premium Denim, Sock & Hosiery, Premier Accessories
- **⚠️ Review Needed (Rating < 3.5):** 3 suppliers - Streetwear Collective (3.4), Quality Basics (3.3), Global Headwear (3.2)

**ESG Compliance Leaders:**
- Urban Threads Wholesale (4.8★, Preferred)
- Fashion Forward Wholesale (4.7★, Preferred)
- Footwear Direct International (4.6★, Preferred)
- Elite Fashion Distributors (4.5★, Preferred)
- Classic Outerwear Imports (4.4★)
- Active Wear Solutions (4.3★)

**Non-Approved Vendors Requiring Review:**
- Global Headwear Co (3.2★, 25-day lead time)
- Streetwear Collective (3.4★, 22-day lead time)
- Quality Basics Wholesale (3.3★, 24-day lead time)

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
- **Net 30:** 14 suppliers (70%)
- **Net 45:** 4 suppliers (20%)
- **Net 60:** 2 suppliers (10%)

### Lead Time Analysis
- **Average Lead Time:** 16.2 days
- **Fastest Delivery:** 9 days (Fashion Forward Wholesale)
- **Longest Lead Time:** 25 days (Global Headwear Co)
- **Express Shipping (≤10 days):** 2 suppliers - Fashion Forward (9 days), Urban Threads (10 days)
- **Standard Shipping (11-15 days):** 9 suppliers
- **Extended Lead Time (16-20 days):** 6 suppliers
- **Slow Delivery (>20 days):** 3 suppliers - Streetwear (22d), Quality Basics (24d), Global Headwear (25d)

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

The GitHub Popup retail system includes two specialized Model Context Protocol (MCP) servers that provide AI agents with access to different aspects of the retail database and operations. Each server runs on a dedicated port and offers specific tools for different business functions.

### 🏦 Finance Agent MCP Server (Port 8002)

**Purpose:** Provides finance-related tools and operations to support finance agents with order policies, contracts, sales analysis, and inventory management.

**Endpoint:** `http://localhost:8002/mcp`

#### Available Tools:

##### 1. `get_company_order_policy`
Get company order processing policies and budget authorization rules. Returns company policies related to order processing, budget authorization, and approval requirements. Policies can be filtered by department.

**Input Parameters:**
- `department` (Optional[str]): Optional department name to filter policies (e.g., "Procurement", "Finance")

**Returns:** JSON string with format `{"c": [columns], "r": [[row data]], "n": count}` containing policy names, types, content, thresholds, and approval requirements.

##### 2. `get_supplier_contract`
Get supplier contract information including terms and conditions. Returns active contract details for a specific supplier including contract numbers, dates, values, payment terms, and renewal status.

**Input Parameters:**
- `supplier_id` (int): The unique identifier for the supplier (required)

**Returns:** JSON string with format `{"c": [columns], "r": [[row data]], "n": count}` containing contract details, dates, values, and calculated expiry information.

##### 3. `get_historical_sales_data`
Get historical sales data with revenue, order counts, and customer metrics. Returns comprehensive sales statistics including total revenue, order counts, average order values, units sold, and unique customer counts. Data can be filtered by store and category.

**Input Parameters:**
- `days_back` (int): Number of days to look back (default: 30)
- `store_id` (Optional[int]): Optional store ID to filter results
- `category_name` (Optional[str]): Optional category name to filter results

**Returns:** JSON string with format `{"c": [columns], "r": [[row data]], "n": count}` containing date, store, category, revenue, orders, and customer metrics.

##### 4. `get_current_inventory_status`
Get current inventory status across stores with values and low stock alerts. Returns inventory levels, cost values, retail values, and low stock alerts for products across all stores. Can be filtered by store and category.

**Input Parameters:**
- `store_id` (Optional[int]): Optional store ID to filter results
- `category_name` (Optional[str]): Optional category name to filter results
- `low_stock_threshold` (int): Stock level below which to trigger alert (default: 10)

**Returns:** JSON string with format `{"c": [columns], "r": [[row data]], "n": count}` containing store, product, category, stock levels, values, and alerts.

##### 5. `get_stores`
Get store information with optional filtering by name. Returns store details including store IDs, names, and online status. Can be filtered by store name using partial, case-insensitive matching.

**Input Parameters:**
- `store_name` (Optional[str]): Optional store name to search for (partial match, case-insensitive)

**Returns:** JSON string with format `{"c": [columns], "r": [[row data]], "n": count}` containing store_id, store_name, is_online, rls_user_id.

##### 6. `get_current_utc_date`
Get the current date and time in UTC format. Useful for calculating date ranges, tracking when analyses were performed, and providing context for time-sensitive financial data.

**Input Parameters:** None

**Returns:** ISO 8601 formatted UTC datetime string (YYYY-MM-DDTHH:MM:SS.ffffffZ)

---

### 🏭 Supplier Agent MCP Server (Port 8001)

**Purpose:** Provides tools to support supplier management operations including supplier discovery, performance analysis, contract management, and policy compliance.

**Endpoint:** `http://localhost:8001/mcp`

#### Available Tools:

##### 1. `find_suppliers_for_request`
Find suppliers that match procurement request requirements. This tool searches for suppliers based on product category, ESG compliance, rating requirements, lead time constraints, and budget considerations. Returns suppliers ranked by preference and performance.

**Input Parameters:**
- `product_category` (Optional[str]): Product category to filter suppliers by (e.g., 'Tools', 'Hardware', 'Building Materials'). Leave empty to search all categories.
- `esg_required` (bool): Whether ESG (Environmental, Social, Governance) compliance is required. Set to true if the request specifically requires ESG-compliant suppliers. (default: false)
- `min_rating` (float): Minimum supplier rating required 0.0 to 5.0. Default is 3.0 for acceptable quality suppliers.
- `max_lead_time` (int): Maximum acceptable lead time in days. Default is 30 days for standard procurement.
- `budget_min` (Optional[float]): Minimum budget amount to consider suppliers with appropriate minimum order amounts.
- `budget_max` (Optional[float]): Maximum budget amount to filter suppliers by bulk discount thresholds.
- `limit` (int): Maximum number of suppliers to return. Default is 10.

**Returns:** JSON with supplier details including ratings, contact info, terms, and contract status.

##### 2. `get_supplier_history_and_performance`
Get detailed supplier performance history and metrics. This tool retrieves historical performance evaluations, procurement activity, and performance trends for a specific supplier. Includes cost, quality, delivery, and compliance scores over time.

**Input Parameters:**
- `supplier_id` (int): Unique identifier of the supplier to get performance history for.
- `months_back` (int): Number of months of history to retrieve. Default is 12 months for annual performance view.

**Returns:** JSON with performance scores, evaluation dates, procurement history, and trend data.

##### 3. `get_supplier_contract`
Get supplier contract details and terms. This tool retrieves active contract information including contract numbers, terms and conditions, payment terms, contract values, expiration dates, and renewal information for a specific supplier.

**Input Parameters:**
- `supplier_id` (int): Unique identifier of the supplier to get contract information for.

**Returns:** JSON with contract details, terms, values, dates, and renewal status.

##### 4. `get_company_supplier_policy`
Get company policies related to supplier management. This tool retrieves company policies and procedures for supplier selection, procurement processes, vendor approval requirements, and budget authorization limits. Helps ensure compliance with company guidelines.

**Input Parameters:**
- `policy_type` (Optional[str]): Type of policy to retrieve. Options: 'procurement', 'vendor_approval', 'budget_authorization', 'order_processing'. Leave empty to get all supplier-related policies.
- `department` (Optional[str]): Department-specific policies to retrieve. Leave empty to get company-wide policies.

**Returns:** JSON with policy documents, procedures, requirements, and approval thresholds.

##### 5. `get_current_utc_date`
Get the current UTC date and time in ISO format. Useful for date-time relative queries or understanding the current date for time-sensitive supplier analysis.

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
2. **Supplier Agent** → Supplier MCP Server (8001) for vendor management and procurement

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

### Database Overview

The GitHub Popup retail system uses a SQLite database located at `data/retail.db`.

**Data Models:**
All data models and table definitions are available in the `app/models/sqlite/` directory.

### Core Tables Overview

The GitHub Popup retail database consists of 15 tables organized into the following functional areas:

1. **Customer Management**: `customers`
2. **Store Management**: `stores` (with RLS user mapping)
3. **Product Catalog**: `categories`, `product_types`, `products`
4. **Order Management**: `orders`, `order_items`
5. **Inventory Management**: `inventory`
6. **Supplier Management**: `suppliers`, `supplier_performance`, `supplier_contracts`
7. **Procurement**: `procurement_requests`, `company_policies`, `approvers`, `notifications`

**Recent Schema Enhancements:**
- **Enhanced Store Model**: Added `is_online` field to distinguish physical vs online stores
- **RLS Integration**: All stores have `rls_user_id` for row-level security
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
- **Active Suppliers:** 20 suppliers (all located in Seattle, WA)
- **ESG Compliance:** 0% of suppliers are ESG compliant
- **Inventory Value:** $233,853.86 total retail value ($214K physical + $20K online)
- **Climate Zones:** 3-zone seasonal system (Pacific Northwest, Temperate, Warm)

### Data Architecture Highlights
- **Row Level Security (RLS):** Multi-tenant database with store-level data isolation
- **Data Models:** Available in `app/models/sqlite/` directory
- **Seasonal Intelligence:** Climate zone-based demand forecasting
- **Supplier Integration:** Comprehensive procurement workflow with bulk discounts
- **Real-time Inventory:** Live stock levels across all store locations

### Use Cases & Applications
- **Store Operations:** Individual store inventory management and sales tracking
- **Corporate Analytics:** Cross-store performance analysis and trend identification
- **Procurement Optimization:** Supplier selection, bulk discount utilization, ESG compliance
- **Seasonal Planning:** Climate-aware inventory planning and seasonal product mix
- **Customer Intelligence:** Purchase pattern analysis and store preference insights

---

## Table Schemas

All table schemas and data models are available in the `app/models/sqlite/` directory.

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

#### Current Stock Distribution by Category

| Category | Product Types | Unique Products | Total Stock | Avg Stock/Product | Inventory Value |
|----------|---------------|-----------------|-------------|-------------------|-----------------|
| **Accessories** | 7 types | 40 | 1,569 units | 39.2 | $44,629 |
| **Apparel - Bottoms** | 3 types | 17 | 610 units | 35.9 | $29,845 |
| **Apparel - Tops** | 5 types | 35 | 1,457 units | 41.6 | $52,422 |
| **Footwear** | 4 types | 22 | 886 units | 40.3 | $65,597 |
| **Outerwear** | 2 types | 14 | 492 units | 35.1 | $41,360 |

**Total Inventory:** 128 products, 5,014 units, $233,853 retail value (Online store only)

#### Product Type Detail

**Accessories** (19% of inventory value):
- **Backpacks & Bags**: 307 units across 9 products ($13,312 value)
- **Belts**: 242 units across 4 products ($7,236 value)
- **Caps & Hats**: 271 units across 8 products ($6,435 value)
- **Socks**: 319 units across 8 products ($4,671 value)
- **Sunglasses**: 154 units across 3 products ($6,589 value)
- **Gloves**: 170 units across 4 products ($3,632 value)
- **Scarves**: 106 units across 4 products ($2,754 value)

**Apparel - Bottoms** (13% of inventory value):
- **Jeans**: 321 units across 9 products ($18,451 value)
- **Pants**: 152 units across 4 products ($6,716 value)
- **Shorts**: 137 units across 4 products ($4,678 value)

**Apparel - Tops** (22% of inventory value):
- **T-Shirts**: 510 units across 12 products ($11,084 value)
- **Formal Shirts**: 287 units across 8 products ($13,092 value)
- **Hoodies**: 301 units across 7 products ($13,070 value)
- **Flannel Shirts**: 163 units across 4 products ($8,233 value)
- **Sweatshirts**: 196 units across 4 products ($6,943 value)

**Footwear** (28% of inventory value):
- **Dress Shoes**: 311 units across 5 products ($29,656 value) - Highest value product type
- **Sneakers**: 310 units across 9 products ($19,849 value)
- **Boots**: 125 units across 5 products ($12,424 value)
- **Sandals**: 140 units across 3 products ($3,669 value)

**Outerwear** (18% of inventory value):
- **Jackets**: 375 units across 10 products ($29,211 value)
- **Coats**: 117 units across 4 products ($12,149 value)

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

### 1. SQLite Database Backend
- **File-based storage**: Single `data/retail.db` file for easy portability and backup
- **Zero configuration**: No server setup required - just connect and query
- **Data models**: Available in `app/models/sqlite/` directory
- **Cross-platform compatibility**: Works on Linux, Windows, and macOS

### 2. Multi-Store Support
- Online store and 15 physical popup locations across major US cities
- Store-specific inventory management and tracking
- Application-layer row-level security for multi-tenant data access

### 3. Comprehensive Product Catalog
- 5 major categories with 21 product types
- 129 unique products with detailed descriptions
- Full supplier integration with cost and pricing information

### 4. Advanced Supplier Management
- ESG compliance tracking for sustainable sourcing
- Performance monitoring and rating system (0-5 scale)
- Contract and procurement workflow management
- Bulk discount programs with varying thresholds

### 5. Robust Approval Workflow
- Multi-level approval processes for procurement
- Department-specific policies and thresholds
- Automated notification system for request tracking

### 6. Seasonal Intelligence
- Comprehensive seasonal sales analysis by category
- Category-specific seasonal patterns across climate zones
- Inventory optimization based on seasonal demand
- Revenue forecasting based on historical trends

---

## Quick Start: Working with the Database

### Connecting to the Database

The database file is located at `data/retail.db`. All data models are available in the `app/models/sqlite/` directory.

### Database File Information

- **Database Path**: `data/retail.db`
- **Data Models**: `app/models/sqlite/`
- **Tables**: 15 tables covering customers, products, orders, inventory, suppliers, and procurement
