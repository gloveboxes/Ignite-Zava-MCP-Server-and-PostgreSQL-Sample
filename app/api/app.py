#!/usr/bin/env python3
"""
FastAPI Backend for GitHub Popup Store
Provides REST API endpoints for the frontend application.
"""

import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import Config
from app.sales_analysis_postgres import PostgreSQLSchemaProvider

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
                    p.discontinued
                FROM retail.products p
                INNER JOIN retail.categories c ON p.category_id = c.category_id
                INNER JOIN retail.product_types pt ON p.type_id = pt.type_id
                LEFT JOIN retail.suppliers s ON p.supplier_id = s.supplier_id
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
                    discontinued=row['discontinued']
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
                    p.discontinued
                FROM retail.products p
                INNER JOIN retail.categories c ON p.category_id = c.category_id
                INNER JOIN retail.product_types pt ON p.type_id = pt.type_id
                LEFT JOIN retail.suppliers s ON p.supplier_id = s.supplier_id
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
                    discontinued=row['discontinued']
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
                    p.discontinued
                FROM retail.products p
                INNER JOIN retail.categories c ON p.category_id = c.category_id
                INNER JOIN retail.product_types pt ON p.type_id = pt.type_id
                LEFT JOIN retail.suppliers s ON p.supplier_id = s.supplier_id
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
                discontinued=row['discontinued']
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
