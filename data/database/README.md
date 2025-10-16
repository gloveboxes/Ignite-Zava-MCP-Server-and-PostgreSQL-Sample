# GitHub Popup Stores PostgreSQL Database Generator

This directory contains the PostgreSQL database generator for **GitHub Popup Stores**, a fictional retail company with popup locations across the US. The generator creates a comprehensive sales database with realistic retail data patterns, seasonal variations, and advanced features for data analysis and agentic applications.

## Quick Start

### How to Generate the GitHub Popup Stores PostgreSQL Database

To generate the complete GitHub Popup Stores PostgreSQL database:

```bash
# Navigate to the database directory
cd data/database

pip install -r requirements.txt

# Run the generator (creates complete database)
python generate_github_postgres.py

# Or run with specific options
python generate_github_postgres.py --show-stats          # Show database statistics
python generate_github_postgres.py --embeddings-only     # Populate embeddings only
python generate_github_postgres.py --verify-embeddings   # Verify embeddings table
python generate_github_postgres.py --verify-seasonal     # Verify seasonal patterns
python generate_github_postgres.py --clear-embeddings    # Clear existing embeddings
python generate_github_postgres.py --batch-size 200      # Set embedding batch size
python generate_github_postgres.py --num-customers 100000 # Set number of customers
python generate_github_postgres.py --help                # Show all options
```

**Prerequisites:**

- PostgreSQL 17+ with pgvector extension
- Python 3.13+ with required packages (asyncpg, faker, python-dotenv)
- Required JSON reference files (see Reference Data Files section below)

### Database Schema Reference

A complete schema backup is available at `/workspace/zava_retail_schema.sql` containing:
- **17 Tables** - Complete retail schema with all column definitions
- **14 Sequences** - Auto-increment sequences for primary keys  
- **60 Indexes** - Performance optimization including vector indexes
- **19 Foreign Key Constraints** - Referential integrity relationships
- **13 RLS Policies** - Row Level Security for multi-tenant access
- **11 Check Constraints** - Data validation constraints

This schema file can be used to recreate the database structure on any PostgreSQL instance with pgvector extension.

## Available Tools

This directory contains several utility tools for managing and working with the GitHub Popup Stores database:

### **Core Database Tools**

- **`generate_github_postgres.py`** - Main database generator that creates the complete GitHub Popup Stores retail database with realistic sales data, seasonal patterns, and AI embeddings
- **`count_products.py`** - Analyzes and reports product counts across categories and embedding status from the JSON reference files

### **AI/ML and Embedding Tools**

- **`add_image_embeddings.py`** - Generates 512-dimensional image embeddings for product images using OpenAI CLIP-ViT-Base-Patch32 model
- **`add_description_embeddings.py`** - Creates 1536-dimensional text embeddings for product descriptions using Azure OpenAI text-embedding-3-small model
- **`query_by_description.py`** - Interactive search tool that finds products using natural language queries via semantic similarity search
- **`image_generation.py`** - Generates product images using Azure OpenAI DALL-E 3 and updates the JSON file with image paths

### **Data Management Tools**

- **`format_embeddings.py`** - Reformats embedding arrays in JSON files to use compact single-line formatting instead of multi-line arrays

### **Documentation**

- **`RLS_USER_GUIDE.md`** & **`row_level_security_guide.md`** - Documentation for Row-Level Security implementation and usage

### **Reference Data Files**

Located in the `reference_data/` directory:

- **`stores_reference.json`** - Consolidated store configurations, product assignments, and seasonal data
- **`product_data.json`** - Complete product catalog with categories, seasonal multipliers, and AI embeddings  
- **`supplier_data.json`** - Supplier information for retail vendors
- **`seasonal_multipliers.json`** - Seasonal adjustment factors for different climate zones

## Overview

The database generator creates a complete retail ecosystem for GitHub Popup Stores, simulating a multi-store retailer with 16 locations across major US cities, including 15 physical popup stores and 1 online store. The generated data supports advanced analytics, seasonal pattern analysis, multimodal AI applications with both image and text embeddings, and agentic applications.

**Key Features:**
- **Static Reference Data**: All supplier information, contract data, and business-critical values are controlled via JSON files for consistent, predictable database generation
- **Reproducible Results**: Static data ensures identical database content across multiple generations for reliable testing and development

## Generated Database Structure

### Available Users

#### 1. `postgres` (Superuser)

- **Username**: `postgres`
- **Password**: `P@ssw0rd!`
- **Privileges**: Superuser (bypasses Row level Security (RLS) by default)
- **Use case**: Database administration, schema creation, data generation
- **Created**: Automatically by PostgreSQL

#### 2. `store_manager` (Regular User)

- **Username**: `store_manager`
- **Password**: `StoreManager123!`
- **Privileges**: Regular user (RLS policies apply)
- **Use case**: Testing RLS policies, simulating application user access
- **Created**: Automatically by `init-db.sh` during database initialization

### Core Tables

#### **Customers** (`retail.customers`)

- **50,000+ customer records** with realistic demographic data
- Customer information: names, emails, phone numbers
- Primary store assignments based on geographic distribution

#### **Stores** (`retail.stores`)

- **16 retail locations** across major US cities:
  - **Physical stores (15)**: NYC Times Square, SF Union Square, Austin Downtown, Denver LoDo, Chicago Loop, Boston Back Bay, Seattle Capitol Hill, Atlanta Midtown, Miami Design District, Portland Pearl District, Nashville Music Row, Phoenix Scottsdale, Minneapolis Mill District, Raleigh Research Triangle, Salt Lake City Downtown
  - **Online store (1)**: GitHub Popup Online Store
- Each store has unique characteristics:
  - Customer distribution weights (traffic patterns)
  - Order frequency multipliers
  - Order value multipliers
  - Geographic and climate zone assignments
- Row-Level Security (RLS) support for store manager access control

#### **Product Catalog** (`retail.categories`, `retail.product_types`, `retail.products`)

- **5 main product categories** with comprehensive retail inventory:
  - **Accessories**: Backpacks & Bags, Belts, Caps & Hats, Gloves, Scarves, Socks, Sunglasses
  - **Apparel - Bottoms**: Jeans, Pants, Shorts
  - **Apparel - Tops**: Flannel Shirts, Formal Shirts, Hoodies, Sweatshirts, T-Shirts
  - **Footwear**: Boots, Dress Shoes, Sandals, Sneakers
  - **Outerwear**: Coats, Jackets
- **129 unique products** across 21 product types
- **Product hierarchy**: Categories → Product Types → Individual Products
- **Cost and pricing structure** with consistent 33% gross margin
- **Complete product specifications**: SKUs, descriptions, pricing
- **Supplier integration**: Full procurement workflow with 20 suppliers using static contract data for consistent results

#### **Orders & Sales** (`retail.orders`, `retail.order_items`)

- **Historical transaction data** spanning 2020-2026
- **Order header** information: customer, store, date
- **Detailed line items**: products, quantities, prices, discounts
- **Variable order patterns** based on store characteristics and seasonality

#### **Inventory** (`retail.inventory`)

- **Store-specific stock levels** for all products
- **Seasonal inventory adjustments** based on demand patterns
- **Geographic distribution** reflecting local market preferences

#### **Product Image Embeddings** (`retail.product_image_embeddings`)

- **AI ready vector embeddings** for product images
- **512-dimensional vectors** using pgvector extension
- **Vector similarity search** capabilities for recommendation systems
- **Image metadata** and embedding relationships

#### **Product Description Embeddings** (`retail.product_description_embeddings`)

- **AI ready vector embeddings** for product descriptions
- **1536-dimensional vectors** using pgvector extension
- **Text-based similarity search** capabilities for recommendation systems
- **Enhanced product discovery** through semantic search

## Key Data Features

### 📊 Seasonal Variations

The generator implements **multi-zone seasonal multipliers** across three climate zones for realistic business patterns:

#### **🌲 Pacific Northwest Zone** (Seattle, Portland)
- **Outerwear**: Peak winter demand (1.8x), low summer (0.6x)
- **Apparel - Tops**: Summer peak (1.4x), winter low (0.6x)
- **Pattern**: Mild, wet winters and dry summers

#### **🌡️ Temperate Zone** (NYC, Denver, Chicago, Boston, Nashville, Minneapolis, Raleigh, Salt Lake City)
- **Outerwear**: Strong winter pattern (1.6x), minimal summer (0.5x)
- **Apparel - Tops**: Summer focused (1.3x), winter low (0.7x)
- **Pattern**: Moderate seasonal variation with distinct seasons

#### **☀️ Warm Zone** (SF, Austin, Atlanta, Miami, Phoenix)
- **Outerwear**: Mild winter demand (1.3x), very low summer (0.4x)
- **Apparel - Tops**: Strong summer demand (1.4x)
- **Pattern**: Milder winters, hot summers

#### **Seasonal Business Intelligence**
- **Outerwear** shows strongest seasonal variation (0.4x to 1.8x multipliers)
- **Apparel - Bottoms** maintain stable year-round demand
- **Q4 (Oct-Dec)** universally strong for outerwear and accessories

### 💰 Financial Structure

#### **Margin Analysis**

- **Consistent 33% gross margin** across all products
- **Cost basis**: JSON price data represents wholesale cost
- **Selling price calculation**: Cost ÷ 0.67 = Retail Price
- **Margin verification**: Built-in reporting and validation

#### **Revenue Patterns**

- **Year-over-year growth**: Configurable growth patterns (2020-2026) with consistent business expansion
- **Growth trajectory**: Steady increases year-over-year, except for 2023 which shows a slight decline reflecting market conditions
- **Store performance variation**: Based on location and market size
- **Seasonal revenue fluctuations**: Aligned with product demand cycles

### 🏪 Store Performance Characteristics

#### **High-Performance Stores**

- **NYC Times Square**: Premium urban location with high traffic
- **SF Union Square**: West coast flagship with strong performance
- **Online Store**: Complete product catalog (129 products) vs curated physical store selection (40-55 products)

#### **Geographic Distribution**

- **15 major US cities** with themed popup locations
- **Strategic positioning**: Tech hubs, cultural districts, downtown cores
- **Market coverage**: East Coast, West Coast, Mountain West, Midwest, South
- **Climate-aware inventory**: Seasonal product mix based on local weather patterns

#### **Store Performance Characteristics**

- **Physical stores**: 40-55 curated products (~30% of total catalog)
- **Online store**: Complete product catalog access
- **Product overlap**: ~20-30% core essentials shared across stores
- **Unique assortment**: 70-80% store-specific products based on local themes

### 🔒 Security & Access Control

#### **Row-Level Security (RLS)**

- **Store manager isolation**: Each manager sees only their store's data
- **Super manager access**: UUID `00000000-0000-0000-0000-000000000000` bypasses all restrictions
- **Secure multi-tenancy**: Perfect for workshop and demo scenarios
- **Policy coverage**: Orders, order items, inventory, customers

#### **Manager Access Patterns**

- **Unique UUIDs** for each store manager
- **Complete data isolation** between stores
- **Controlled access** to reference data (products, categories)

### 🚀 Advanced Features

#### **Vector Search Capabilities**

- **pgvector integration** for similarity search
- **Product image embeddings** (512-dimensional) for visual recommendation engines
- **Product description embeddings** (1536-dimensional) for semantic text search
- **Optimized vector indexes** for performance
- **Dual embedding support** ready for multimodal ML applications

#### **Performance Optimization**

- **Comprehensive indexing strategy**: 20+ optimized indexes
- **Covering indexes** for common query patterns
- **Batch insert operations** for large data volumes
- **Query performance monitoring** and optimization

#### **Data Quality & Validation**

- **Built-in verification** routines for data consistency
- **Seasonal pattern validation** and reporting
- **Margin analysis** and financial reconciliation
- **Statistical summaries** and health checks

## Technical Requirements

- **PostgreSQL 17+** with pgvector extension
- **Python 3.13+** with asyncpg, faker, python-dotenv
- **Database**: `zava` with `retail` schema
- **Memory**: Recommended 4GB+ for large datasets
- **Storage**: ~2GB for complete database with embeddings

## Reference Data Files

### `reference_data/stores_reference.json`

- Consolidated store configurations and product assignments
- Store location data with climate zone assignments
- Customer distribution weights and performance multipliers
- Store manager RLS UUID mappings
- Product assignments for each store

### `reference_data/product_data.json`

- Complete product catalog with categories and types
- Product specifications, pricing, and descriptions
- Image and description embedding data for AI/ML applications
- SKUs and supplier relationships

### `reference_data/supplier_data.json`

- **20 supplier profiles** with complete static data for consistent database generation
- **Static supplier information**: IDs, names, codes, and contact details
- **Contract management**: Contract numbers, values, and end dates
- **Procurement workflow**: ESG compliance status, vendor approval data, bulk discount thresholds, payment terms, performance ratings, and lead times
- **Consistent data generation**: All supplier-related fields use static values from JSON instead of random generation

### `reference_data/seasonal_multipliers.json`

- Climate zone definitions (Pacific Northwest, Temperate, Warm)
- Monthly seasonal multipliers by category and zone
- Store-to-climate-zone mappings

## Data Volume Summary

| Component | Count | Description |
|-----------|-------|-------------|
| **Customers** | 50,000+ | Realistic demographic profiles across 15 US cities and online |
| **Products** | 129 | Complete retail catalog (accessories, apparel, footwear, outerwear) |
| **Product Images** | 129 | Product images linked to database for image-based searches |
| **Stores** | 16 | 15 physical popup stores + 1 online store across major US cities |
| **Suppliers** | 20 | Complete supplier directory with static contract data and procurement workflow |
| **Orders** | 200,000+ | Multi-year transaction history with detailed sales data |
| **Inventory Items** | 3,000+ | Store-specific inventory across multiple locations |
| **Image Embeddings** | 129 | AI-powered image similarity searches using OpenAI CLIP-ViT-Base-Patch32 |
| **Description Embeddings** | 129 | AI-powered text similarity searches using text-embedding-3-small |

This database provides a realistic foundation for retail analytics, machine learning experimentation, seasonal trend analysis, and multi-tenant application development in the retail industry. The database supports PostgreSQL with pgvector extension, enabling advanced AI-powered product similarity searches, comprehensive sales analytics, and sophisticated procurement workflows.

## JSON Data File Schemas

The generator requires two JSON configuration files that define the product catalog and store configurations:

### `reference_data/product_data.json` Schema

Defines the complete product catalog with embeddings and seasonal patterns:

```json
{
  "main_categories": {
    "<CATEGORY_NAME>": {
      "<PRODUCT_TYPE>": [
        {
          "name": "string",                    // Product display name
          "sku": "string",                     // Unique product identifier
          "price": number,                     // Base cost price
          "description": "string",             // Product description
          "stock_level": number,               // Base inventory level
          "image_path": "string",              // Relative path to product image
          "image_embedding": [float, ...],     // 512-dimension image vector embedding
          "description_embedding": [float, ...] // 1536-dimension text vector embedding
        }
      ]
    }
  }
}
```

**Key Points:**

- `image_embedding`: 512-dimensional vector for image similarity search with pgvector
- `description_embedding`: 1536-dimensional vector for text similarity search with pgvector
- `price`: Treated as wholesale cost; retail price calculated with 33% gross margin
- Each category can contain multiple product types, each with an array of products
- Seasonal multipliers are now defined separately in `seasonal_multipliers.json`

### `reference_data/stores_reference.json` Schema

Defines store configurations and business rules:

```json
{
  "stores": {
    "<STORE_NAME>": {
      "rls_user_id": "uuid",                  // Row Level Security identifier
      "customer_distribution_weight": number, // Relative customer allocation weight
      "order_frequency_multiplier": number,   // Order frequency scaling factor
      "order_value_multiplier": number        // Order value scaling factor
    }
  },
  "year_weights": {
    "<YEAR>": number                          // Growth pattern weights by year
  }
}
```

**Key Points:**

- `rls_user_id`: UUID for Row Level Security policies (store manager access control)
- Distribution weights: Control customer and sales allocation across stores
- Order multipliers: Scale order frequency and value by store characteristics
- Year weights: Create realistic business growth patterns over time (2020-2026)

### `reference_data/supplier_data.json` Schema

Defines comprehensive supplier profiles with static contract data for consistent database generation:

```json
{
  "<SUPPLIER_ID>": {
    "supplier_id": number,                    // Sequential supplier ID (1-20)
    "supplier_name": "string",               // Company name
    "supplier_code": "string",               // Standard format: SUP001-SUP020
    "contact_email": "string",               // Primary contact email
    "contact_phone": "string",               // Primary contact phone
    "contracts": [
      {
        "contract_id": number,               // Contract identifier
        "contract_number": "string",         // Format: 2024-XXXX-NNN
        "contract_value": number,            // Contract value (rounded to $10K)
        "start_date": "YYYY-MM-DD",          // Contract start date
        "end_date": "YYYY-MM-DD",            // Contract end date (1-2 years)
        "contract_status": "active",         // Contract status
        "payment_terms": "string",           // Payment terms (Net 30/45/60)
        "auto_renew": boolean,               // Auto-renewal flag
        "contract_created": "ISO datetime",  // Creation timestamp
        "renewal_due_soon": boolean,         // Renewal alert flag
        "days_until_expiry": number          // Calculated days to expiry
      }
    ]
  }
}
```

**Key Points:**

- **Static Data Control**: All supplier information is now static and controlled via JSON instead of random generation
- **Contract Values**: Rounded to nearest $10,000 ranging from $50K to $600K for realistic contract sizes
- **Contract Dates**: End dates range between 1-2 years from current date for realistic contract terms
- **Contract Numbers**: Follow standard format `2024-XXXX-NNN` for consistent naming convention
- **Supplier Codes**: Sequential format `SUP001` through `SUP020` for easy identification
- **Supplier IDs**: Sequential integers 1-20 matching database primary keys
- **Database Consistency**: Generator uses these static values to ensure identical data across database recreations

### Database Connection Configuration

The generator connects to PostgreSQL using these default settings:

- **Host**: `db` (Docker container)
- **Port**: `5432`
- **Database**: `zava`
- **Schema**: `retail`
- **User**: `postgres`
- **Password**: `P@ssw0rd!`

Connection settings can be overridden using environment variables or a `.env` file.

## Database Schema Reference

The complete database schema is available in `/workspace/zava_retail_schema.sql`. This file contains the full DDL (Data Definition Language) for recreating the entire database structure.

### Schema Highlights

#### **Core Tables (17 total)**
- `retail.stores` - Store locations with RLS user mappings
- `retail.customers` - Customer profiles with store associations
- `retail.categories` - Product category hierarchy
- `retail.product_types` - Product type definitions within categories
- `retail.products` - Complete product catalog with supplier relationships
- `retail.suppliers` - Supplier directory with procurement terms
- `retail.orders` - Order header information
- `retail.order_items` - Detailed line items for each order
- `retail.inventory` - Store-specific stock levels
- `retail.supplier_performance` - Supplier evaluation and ratings
- `retail.procurement_requests` - Purchase requisition workflow
- `retail.company_policies` - Business rules and approval policies
- `retail.supplier_contracts` - Contract management
- `retail.approvers` - Approval authority definitions
- `retail.notifications` - System notifications
- `retail.product_image_embeddings` - AI image vector embeddings (512-dim)
- `retail.product_description_embeddings` - AI text vector embeddings (1536-dim)

#### **Advanced Features**
- **Row Level Security (RLS)**: Multi-tenant data isolation with store-specific access control
- **Vector Search**: pgvector integration for AI-powered product similarity searches
- **Performance Optimization**: 60+ indexes including covering indexes and vector indexes
- **Data Integrity**: 19 foreign key constraints and 11 check constraints
- **Seasonal Intelligence**: Climate zone-based seasonal multipliers
- **Procurement Workflow**: Complete supplier management and approval processes

#### **Usage**
```bash
# Restore schema to a new PostgreSQL database
psql -h localhost -U postgres -d your_database -f /workspace/zava_retail_schema.sql

# Or use with Docker
docker exec -i postgres_container psql -U postgres -d zava < /workspace/zava_retail_schema.sql
```

The schema file includes all necessary DDL statements to recreate the complete database structure on any PostgreSQL 17+ instance with the pgvector extension.
