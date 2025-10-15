#!/usr/bin/env python3
"""
FastAPI Backend for GitHub Popup Store
Provides REST API endpoints for the frontend application.
"""

import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from agent_framework import ChatMessage, WorkflowOutputEvent, WorkflowStartedEvent
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json

from app.config import Config
from app.sales_analysis_postgres import PostgreSQLSchemaProvider
from app.agents.stock import workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
config = Config()
SCHEMA_NAME = "retail"
RLS_USER_ID = ""  # Empty for no RLS restrictions

# Database connection
db_provider: Optional[PostgreSQLSchemaProvider] = None


# Pydantic models for API responses
class Product(BaseModel):
    """Product model for API responses"""
    product_id: int = Field(..., description="Unique product identifier")
    sku: str = Field(..., description="Stock keeping unit")
    product_name: str = Field(..., description="Product display name")
    category_name: str = Field(..., description="Product category")
    type_name: str = Field(..., description="Product type")
    unit_price: float = Field(..., description="Retail price")
    cost: float = Field(..., description="Product cost")
    gross_margin_percent: float = Field(..., description="Profit margin percentage")
    product_description: Optional[str] = Field(None, description="Product description")
    supplier_name: Optional[str] = Field(None, description="Supplier name")
    discontinued: bool = Field(False, description="Product availability status")
    image_url: Optional[str] = Field(None, description="Product image URL")


class ProductList(BaseModel):
    """List of products response"""
    products: List[Product]
    total: int


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown events"""
    global db_provider

    # Startup
    logger.info("🚀 Starting GitHub API Server...")
    try:
        db_provider = PostgreSQLSchemaProvider()
        await db_provider.create_pool()
        logger.info("✅ Database connection pool created")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down GitHub API Server...")
    if db_provider:
        await db_provider.close_pool()
        logger.info("✅ Database connection pool closed")


# Create FastAPI app
app = FastAPI(
    title="GitHub Popup Store API",
    description="REST API for GitHub popup merchandise store",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = (
        "connected"
        if db_provider and db_provider.connection_pool
        else "disconnected"
    )
    return {
        "status": "healthy",
        "service": "github-api",
        "database": db_status
    }


# Featured products endpoint
@app.get("/api/products/featured", response_model=ProductList)
async def get_featured_products(
    limit: int = Query(8, ge=1, le=50, description="Number of products to return")
):
    """
    Get featured products for the homepage.
    Returns a curated selection of products with good ratings and availability.
    """
    if not db_provider or not db_provider.connection_pool:
        raise HTTPException(
            status_code=503,
            detail="Database connection not available"
        )

    try:
        conn = await db_provider.get_connection()

        try:
            # Set RLS user if needed
            if RLS_USER_ID:
                await conn.execute(
                    "SELECT set_config('app.current_rls_user_id', $1, false)",
                    RLS_USER_ID
                )

            # Query for featured products
            # Strategy: Get products with good variety across categories
            # Prefer products with higher margins (more popular/profitable)
            # Exclude discontinued items
            query = """
                SELECT
                    p.product_id,
                    p.sku,
                    p.product_name,
                    c.category_name,
                    pt.type_name,
                    p.base_price as unit_price,
                    p.cost,
                    p.gross_margin_percent,
                    p.product_description,
                    s.supplier_name,
                    p.discontinued,
                    pie.image_url
                FROM retail.products p
                INNER JOIN retail.categories c ON p.category_id = c.category_id
                INNER JOIN retail.product_types pt ON p.type_id = pt.type_id
                LEFT JOIN retail.suppliers s ON p.supplier_id = s.supplier_id
                LEFT JOIN retail.product_image_embeddings pie ON p.product_id = pie.product_id
                WHERE p.discontinued = false
                ORDER BY p.gross_margin_percent DESC, RANDOM()
                LIMIT $1
            """
            
            rows = await conn.fetch(query, limit)
            
            products = []
            for row in rows:
                products.append(Product(
                    product_id=row['product_id'],
                    sku=row['sku'],
                    product_name=row['product_name'],
                    category_name=row['category_name'],
                    type_name=row['type_name'],
                    unit_price=float(row['unit_price']),
                    cost=float(row['cost']),
                    gross_margin_percent=float(row['gross_margin_percent']),
                    product_description=row['product_description'],
                    supplier_name=row['supplier_name'],
                    discontinued=row['discontinued'],
                    image_url=row['image_url']
                ))
            
            logger.info(f"✅ Retrieved {len(products)} featured products")
            
            return ProductList(
                products=products,
                total=len(products)
            )
            
        finally:
            await db_provider.release_connection(conn)
            
    except Exception as e:
        logger.error(f"❌ Error fetching featured products: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch featured products: {str(e)}"
        )


# Get products by category endpoint
@app.get("/api/products/category/{category}", response_model=ProductList)
async def get_products_by_category(
    category: str,
    limit: int = Query(50, ge=1, le=100, description="Max products to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Get products filtered by category.
    Category names: Accessories, Apparel - Bottoms, Apparel - Tops, Footwear, Outerwear
    """
    if not db_provider or not db_provider.connection_pool:
        raise HTTPException(
            status_code=503,
            detail="Database connection not available"
        )

    try:
        conn = await db_provider.get_connection()

        try:
            # Set RLS user if needed
            if RLS_USER_ID:
                await conn.execute(
                    "SELECT set_config('app.current_rls_user_id', $1, false)",
                    RLS_USER_ID
                )

            # Query products by category
            query = """
                SELECT
                    p.product_id,
                    p.sku,
                    p.product_name,
                    c.category_name,
                    pt.type_name,
                    p.base_price as unit_price,
                    p.cost,
                    p.gross_margin_percent,
                    p.product_description,
                    s.supplier_name,
                    p.discontinued,
                    pie.image_url
                FROM retail.products p
                INNER JOIN retail.categories c ON p.category_id = c.category_id
                INNER JOIN retail.product_types pt ON p.type_id = pt.type_id
                LEFT JOIN retail.suppliers s ON p.supplier_id = s.supplier_id
                LEFT JOIN retail.product_image_embeddings pie ON p.product_id = pie.product_id
                WHERE p.discontinued = false
                    AND LOWER(c.category_name) = LOWER($1)
                ORDER BY p.product_name
                LIMIT $2 OFFSET $3
            """

            rows = await conn.fetch(query, category, limit, offset)

            if not rows:
                # Check if category exists
                category_check = await conn.fetchval(
                    """SELECT COUNT(*) FROM retail.categories
                       WHERE LOWER(category_name) = LOWER($1)""",
                    category
                )
                if category_check == 0:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Category '{category}' not found"
                    )

            products = []
            for row in rows:
                products.append(Product(
                    product_id=row['product_id'],
                    sku=row['sku'],
                    product_name=row['product_name'],
                    category_name=row['category_name'],
                    type_name=row['type_name'],
                    unit_price=float(row['unit_price']),
                    cost=float(row['cost']),
                    gross_margin_percent=float(row['gross_margin_percent']),
                    product_description=row['product_description'],
                    supplier_name=row['supplier_name'],
                    discontinued=row['discontinued'],
                    image_url=row['image_url']
                ))

            logger.info(
                f"✅ Retrieved {len(products)} products for category '{category}'"
            )

            return ProductList(
                products=products,
                total=len(products)
            )

        finally:
            await db_provider.release_connection(conn)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching products by category: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch products: {str(e)}"
        )


# Get product by ID endpoint
@app.get("/api/products/{product_id}", response_model=Product)
async def get_product_by_id(product_id: int):
    """
    Get a single product by its ID.
    Returns complete product information including category, type, and supplier.
    """
    if not db_provider or not db_provider.connection_pool:
        raise HTTPException(
            status_code=503,
            detail="Database connection not available"
        )

    try:
        conn = await db_provider.get_connection()

        try:
            # Set RLS user if needed
            if RLS_USER_ID:
                await conn.execute(
                    "SELECT set_config('app.current_rls_user_id', $1, false)",
                    RLS_USER_ID
                )

            # Query single product by ID
            query = """
                SELECT
                    p.product_id,
                    p.sku,
                    p.product_name,
                    c.category_name,
                    pt.type_name,
                    p.base_price as unit_price,
                    p.cost,
                    p.gross_margin_percent,
                    p.product_description,
                    s.supplier_name,
                    p.discontinued,
                    pie.image_url
                FROM retail.products p
                INNER JOIN retail.categories c ON p.category_id = c.category_id
                INNER JOIN retail.product_types pt ON p.type_id = pt.type_id
                LEFT JOIN retail.suppliers s ON p.supplier_id = s.supplier_id
                LEFT JOIN retail.product_image_embeddings pie ON p.product_id = pie.product_id
                WHERE p.product_id = $1
            """

            row = await conn.fetchrow(query, product_id)

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with ID {product_id} not found"
                )

            product = Product(
                product_id=row['product_id'],
                sku=row['sku'],
                product_name=row['product_name'],
                category_name=row['category_name'],
                type_name=row['type_name'],
                unit_price=float(row['unit_price']),
                cost=float(row['cost']),
                gross_margin_percent=float(row['gross_margin_percent']),
                product_description=row['product_description'],
                supplier_name=row['supplier_name'],
                discontinued=row['discontinued'],
                image_url=row['image_url']
            )

            logger.info(f"✅ Retrieved product {product_id}: {product.product_name}")

            return product

        finally:
            await db_provider.release_connection(conn)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching product {product_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch product: {str(e)}"
        )


@app.get("/api/management/dashboard/top-categories")
async def get_top_categories(limit: int = Query(5, ge=1, le=10, description="Number of top categories to return")):
    """
    Get top categories by total inventory value (cost * stock).
    Returns categories ranked by revenue potential.
    """
    if db_provider is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    try:
        conn = await db_provider.get_connection()
        try:
            logger.info(f"📊 Fetching top {limit} categories by inventory value...")

            query = """
                SELECT
                    c.category_name,
                    COUNT(DISTINCT p.product_id) as product_count,
                    SUM(i.stock_level) as total_stock,
                    SUM(i.stock_level * p.cost) as total_cost_value,
                    SUM(i.stock_level * p.base_price) as total_retail_value,
                    SUM(i.stock_level * (p.base_price - p.cost)) as potential_profit
                FROM retail.inventory i
                JOIN retail.products p ON i.product_id = p.product_id
                JOIN retail.categories c ON p.category_id = c.category_id
                WHERE p.discontinued = false
                GROUP BY c.category_name
                ORDER BY total_retail_value DESC
                LIMIT $1
            """

            rows = await conn.fetch(query, limit)
            
            if not rows:
                return {
                    "categories": [],
                    "total": 0,
                    "max_value": 0
                }

            # Calculate max value for percentage calculation
            max_value = float(rows[0]['total_retail_value']) if rows else 0
            
            categories = []
            for row in rows:
                retail_value = float(row['total_retail_value'])
                percentage = round((retail_value / max_value * 100), 1) if max_value > 0 else 0
                
                categories.append({
                    "name": row['category_name'],
                    "revenue": round(retail_value, 2),
                    "percentage": percentage,
                    "product_count": row['product_count'],
                    "total_stock": row['total_stock'],
                    "cost_value": round(float(row['total_cost_value']), 2),
                    "potential_profit": round(float(row['potential_profit']), 2)
                })

            logger.info(f"✅ Retrieved {len(categories)} categories")

            return {
                "categories": categories,
                "total": len(categories),
                "max_value": round(max_value, 2)
            }

        finally:
            await db_provider.release_connection(conn)

    except Exception as e:
        logger.error(f"❌ Error fetching top categories: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch top categories: {str(e)}"
        )


@app.get("/api/management/suppliers")
async def get_suppliers():
    """
    Get all suppliers with their details and associated product categories.
    Returns comprehensive supplier information for management interface.
    """
    if db_provider is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    try:
        conn = await db_provider.get_connection()
        try:
            logger.info("📊 Fetching suppliers...")

            query = """
                SELECT
                    s.supplier_id,
                    s.supplier_name,
                    s.supplier_code,
                    s.contact_email,
                    s.contact_phone,
                    s.city,
                    s.state_province,
                    s.payment_terms,
                    s.lead_time_days,
                    s.minimum_order_amount,
                    s.bulk_discount_percent,
                    s.supplier_rating,
                    s.esg_compliant,
                    s.approved_vendor,
                    s.preferred_vendor,
                    s.active_status,
                    ARRAY_AGG(DISTINCT c.category_name) 
                        FILTER (WHERE c.category_name IS NOT NULL) as categories
                FROM retail.suppliers s
                LEFT JOIN retail.products p ON s.supplier_id = p.supplier_id
                LEFT JOIN retail.categories c ON p.category_id = c.category_id
                WHERE s.active_status = true
                GROUP BY s.supplier_id
                ORDER BY s.preferred_vendor DESC, s.supplier_rating DESC, s.supplier_name
            """

            rows = await conn.fetch(query)

            suppliers = []
            for row in rows:
                # Format location
                location = f"{row['city']}, {row['state_province']}" if row['city'] else "N/A"
                
                suppliers.append({
                    "id": row['supplier_id'],
                    "name": row['supplier_name'],
                    "code": row['supplier_code'],
                    "location": location,
                    "contact": row['contact_email'],
                    "phone": row['contact_phone'] or "N/A",
                    "rating": float(row['supplier_rating']) if row['supplier_rating'] else 0.0,
                    "esgCompliant": row['esg_compliant'],
                    "approved": row['approved_vendor'],
                    "preferred": row['preferred_vendor'],
                    "categories": row['categories'] or [],
                    "leadTime": row['lead_time_days'],
                    "paymentTerms": row['payment_terms'],
                    "minOrder": float(row['minimum_order_amount']) if row['minimum_order_amount'] else 0,
                    "bulkDiscount": float(row['bulk_discount_percent']) if row['bulk_discount_percent'] else 0
                })

            logger.info(f"✅ Retrieved {len(suppliers)} suppliers")

            return {
                "suppliers": suppliers,
                "total": len(suppliers)
            }

        finally:
            await db_provider.release_connection(conn)

    except Exception as e:
        logger.error(f"❌ Error fetching suppliers: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch suppliers: {str(e)}"
        )


@app.get("/api/management/inventory")
async def get_inventory(
    store_id: int = None,
    category: str = None,
    low_stock_only: bool = False,
    limit: int = 100
):
    """
    Get inventory levels across stores with product and category details.
    
    Args:
        store_id: Optional filter by specific store
        category: Optional filter by product category
        low_stock_only: Show only items with stock below reorder threshold
        limit: Maximum number of records to return
    """
    conn = await db_provider.get_connection()
    
    try:
        logger.info(f"📦 Fetching inventory (store={store_id}, category={category}, low_stock={low_stock_only})...")

        # Build dynamic WHERE clause
        where_conditions = []
        params = []
        param_idx = 1

        if store_id is not None:
            where_conditions.append(f"st.store_id = ${param_idx}")
            params.append(store_id)
            param_idx += 1

        if category:
            where_conditions.append(f"LOWER(c.category_name) = LOWER(${param_idx})")
            params.append(category)
            param_idx += 1

        # For low stock, we'll filter after the query since reorder_point may vary
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        query = f"""
            SELECT
                i.store_id,
                st.store_name,
                st.is_online,
                i.product_id,
                p.product_name,
                p.sku,
                c.category_name,
                pt.type_name,
                i.stock_level,
                p.base_price,
                p.cost,
                s.supplier_name,
                s.supplier_code,
                s.lead_time_days,
                pie.image_url
            FROM retail.inventory i
            INNER JOIN retail.stores st ON i.store_id = st.store_id
            INNER JOIN retail.products p ON i.product_id = p.product_id
            INNER JOIN retail.categories c ON p.category_id = c.category_id
            INNER JOIN retail.product_types pt ON p.type_id = pt.type_id
            LEFT JOIN retail.suppliers s ON p.supplier_id = s.supplier_id
            LEFT JOIN retail.product_image_embeddings pie ON p.product_id = pie.product_id
            {where_clause}
            ORDER BY i.stock_level ASC, st.store_name, p.product_name
            LIMIT ${param_idx}
        """

        params.append(limit)
        rows = await conn.fetch(query, *params)

        inventory_items = []
        for row in rows:
            stock_level = row['stock_level']
            # Calculate reorder point as 20% of typical stock (simple heuristic)
            # In production, this would come from a products or inventory_settings table
            reorder_point = 50  # Default threshold
            
            is_low_stock = stock_level < reorder_point
            
            # Skip if filtering for low stock only
            if low_stock_only and not is_low_stock:
                continue
            
            # Calculate inventory value
            stock_value = float(row['cost']) * stock_level if row['cost'] else 0
            retail_value = float(row['base_price']) * stock_level if row['base_price'] else 0
            
            # Extract location from store name
            # Format: "Zava Pop-Up Location Name" or "Zava Online Store"
            store_location = "Online Store"
            if row['is_online']:
                store_location = "Online Warehouse"
            else:
                # Extract location from name (e.g., "Zava Pop-Up Bellevue Square" -> "Bellevue Square")
                name_parts = row['store_name'].split('Pop-Up ')
                if len(name_parts) > 1:
                    store_location = name_parts[1]
                else:
                    store_location = row['store_name']
            
            inventory_items.append({
                "storeId": row['store_id'],
                "storeName": row['store_name'],
                "storeLocation": store_location,
                "isOnline": row['is_online'],
                "productId": row['product_id'],
                "productName": row['product_name'],
                "sku": row['sku'],
                "category": row['category_name'],
                "type": row['type_name'],
                "stockLevel": stock_level,
                "reorderPoint": reorder_point,
                "isLowStock": is_low_stock,
                "unitCost": float(row['cost']) if row['cost'] else 0,
                "unitPrice": float(row['base_price']) if row['base_price'] else 0,
                "stockValue": round(stock_value, 2),
                "retailValue": round(retail_value, 2),
                "supplierName": row['supplier_name'],
                "supplierCode": row['supplier_code'],
                "leadTime": row['lead_time_days'],
                "imageUrl": row['image_url']
            })

        # Calculate summary statistics
        total_items = len(inventory_items)
        low_stock_count = sum(1 for item in inventory_items if item['isLowStock'])
        total_stock_value = sum(item['stockValue'] for item in inventory_items)
        total_retail_value = sum(item['retailValue'] for item in inventory_items)

        logger.info(f"✅ Retrieved {total_items} inventory items ({low_stock_count} low stock)")

        return {
            "inventory": inventory_items,
            "summary": {
                "totalItems": total_items,
                "lowStockCount": low_stock_count,
                "totalStockValue": round(total_stock_value, 2),
                "totalRetailValue": round(total_retail_value, 2),
                "avgStockLevel": round(sum(item['stockLevel'] for item in inventory_items) / total_items, 1) if total_items > 0 else 0
            }
        }

    except Exception as e:
        logger.error(f"❌ Error fetching inventory: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch inventory: {str(e)}"
        )
    finally:
        await db_provider.release_connection(conn)


@app.get("/api/management/products")
async def get_products(
    category: str = None,
    supplier_id: int = None,
    discontinued: bool = None,
    search: str = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Get products with detailed information including pricing, suppliers, and stock status.
    
    Args:
        category: Filter by category name
        supplier_id: Filter by supplier
        discontinued: Filter by discontinued status
        search: Search in product name, SKU, or description
        limit: Maximum number of records
        offset: Pagination offset
    """
    conn = await db_provider.get_connection()
    
    try:
        logger.info(f"📦 Fetching products...")

        # Build WHERE conditions
        where_conditions = ["1=1"]
        params = []
        param_idx = 1

        if category:
            where_conditions.append(f"LOWER(c.category_name) = LOWER(${param_idx})")
            params.append(category)
            param_idx += 1

        if supplier_id is not None:
            where_conditions.append(f"p.supplier_id = ${param_idx}")
            params.append(supplier_id)
            param_idx += 1

        if discontinued is not None:
            where_conditions.append(f"p.discontinued = ${param_idx}")
            params.append(discontinued)
            param_idx += 1

        if search:
            where_conditions.append(
                f"(LOWER(p.product_name) LIKE LOWER(${param_idx}) OR " +
                f"LOWER(p.sku) LIKE LOWER(${param_idx}) OR " +
                f"LOWER(p.product_description) LIKE LOWER(${param_idx}))"
            )
            params.append(f"%{search}%")
            param_idx += 1

        where_clause = "WHERE " + " AND ".join(where_conditions)

        # Get total count
        count_query = f"""
            SELECT COUNT(*)
            FROM retail.products p
            INNER JOIN retail.categories c ON p.category_id = c.category_id
            LEFT JOIN retail.suppliers s ON p.supplier_id = s.supplier_id
            {where_clause}
        """
        total_count = await conn.fetchval(count_query, *params)

        # Get products with aggregated stock info
        query = f"""
            SELECT
                p.product_id,
                p.sku,
                p.product_name,
                p.product_description,
                c.category_name,
                pt.type_name,
                p.base_price,
                p.cost,
                p.gross_margin_percent,
                p.discontinued,
                s.supplier_id,
                s.supplier_name,
                s.supplier_code,
                s.lead_time_days,
                COALESCE(SUM(i.stock_level), 0) as total_stock,
                COUNT(i.store_id) as store_count,
                pie.image_url
            FROM retail.products p
            INNER JOIN retail.categories c ON p.category_id = c.category_id
            INNER JOIN retail.product_types pt ON p.type_id = pt.type_id
            LEFT JOIN retail.suppliers s ON p.supplier_id = s.supplier_id
            LEFT JOIN retail.inventory i ON p.product_id = i.product_id
            LEFT JOIN retail.product_image_embeddings pie ON p.product_id = pie.product_id
            {where_clause}
            GROUP BY p.product_id, c.category_name, pt.type_name, s.supplier_id, s.supplier_name, s.supplier_code, s.lead_time_days, pie.image_url
            ORDER BY p.product_name
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """

        params.extend([limit, offset])
        rows = await conn.fetch(query, *params)

        products = []
        for row in rows:
            base_price = float(row['base_price']) if row['base_price'] else 0
            cost = float(row['cost']) if row['cost'] else 0
            margin = float(row['gross_margin_percent']) if row['gross_margin_percent'] else 0
            total_stock = int(row['total_stock'])
            
            # Calculate inventory value
            stock_value = cost * total_stock
            retail_value = base_price * total_stock
            
            products.append({
                "productId": row['product_id'],
                "sku": row['sku'],
                "name": row['product_name'],
                "description": row['product_description'],
                "category": row['category_name'],
                "type": row['type_name'],
                "basePrice": base_price,
                "cost": cost,
                "margin": margin,
                "discontinued": row['discontinued'],
                "supplierId": row['supplier_id'],
                "supplierName": row['supplier_name'],
                "supplierCode": row['supplier_code'],
                "leadTime": row['lead_time_days'],
                "totalStock": total_stock,
                "storeCount": int(row['store_count']),
                "stockValue": round(stock_value, 2),
                "retailValue": round(retail_value, 2),
                "imageUrl": row['image_url']
            })

        logger.info(f"✅ Retrieved {len(products)} products (total: {total_count})")

        return {
            "products": products,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "hasMore": (offset + len(products)) < total_count
            }
        }

    except Exception as e:
        logger.error(f"❌ Error fetching products: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch products: {str(e)}"
        )
    finally:
        await db_provider.release_connection(conn)


@app.websocket("/ws/ai-agent/inventory")
async def websocket_ai_agent_inventory(websocket: WebSocket):
    """
    WebSocket endpoint for AI Inventory Agent.
    Streams workflow events back to the frontend in real-time.
    """
    await websocket.accept()
    
    try:
        # Receive the initial request from the client
        data = await websocket.receive_text()
        request_data = json.loads(data)
        
        logger.info(f"🤖 AI Agent request: {request_data.get('message', 'No message')}")
        
        # Send initial acknowledgment
        await websocket.send_json({
            "type": "started",
            "message": "AI Agent workflow initiated...",
            "timestamp": None
        })
        
        # Run the workflow and stream events
        input_message: str = request_data.get("message", "Analyze inventory and recommend restocking priorities")
        input: ChatMessage = ChatMessage(role='user', text=input_message)

        workflow_output = None
        try:
            async for event in workflow.run_stream(input):
                if isinstance(event, WorkflowStartedEvent):
                    event_data = {
                        "type": "workflow_started",
                        "event": str(event.data),
                        "timestamp": None
                    }
                elif isinstance(event, WorkflowOutputEvent):
                    # Capture the workflow output (markdown result)
                    workflow_output = str(event.data)
                    event_data = {
                        "type": "workflow_output",
                        "event": workflow_output,
                        "timestamp": None
                    }
                else:
                    # Stream each workflow event to the frontend
                    event_data = {
                        "type": "event",
                        "event": str(event),
                        "timestamp": None
                    }
                await websocket.send_json(event_data)
                logger.info(f"📤 Sent event: {event}")
            
            # Send completion message with the workflow output
            await websocket.send_json({
                "type": "completed",
                "message": "Workflow completed successfully",
                "output": workflow_output,
                "timestamp": None
            })
            logger.info("✅ AI Agent workflow completed")
            
        except Exception as workflow_error:
            logger.error(f"❌ Workflow error: {workflow_error}")
            await websocket.send_json({
                "type": "error",
                "message": f"Workflow error: {str(workflow_error)}",
                "timestamp": None
            })
    
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket disconnected")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e),
                "timestamp": None
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "GitHub Popup Store API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "featured_products": "/api/products/featured",
            "products_by_category": "/api/products/category/{category}",
            "product_by_id": "/api/products/{product_id}",
            "top_categories": "/api/management/dashboard/top-categories",
            "suppliers": "/api/management/suppliers",
            "inventory": "/api/management/inventory",
            "products": "/api/management/products",
            "ai_agent_inventory": "ws://localhost:8091/ws/ai-agent/inventory (WebSocket)",
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8091,
        log_level="info"
    )
