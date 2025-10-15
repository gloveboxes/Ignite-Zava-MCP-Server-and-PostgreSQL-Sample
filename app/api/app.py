#!/usr/bin/env python3
"""
FastAPI Backend for Zava Popup Store
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
    logger.info("🚀 Starting Zava API Server...")
    try:
        db_provider = PostgreSQLSchemaProvider()
        await db_provider.create_pool()
        logger.info("✅ Database connection pool created")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down Zava API Server...")
    if db_provider:
        await db_provider.close_pool()
        logger.info("✅ Database connection pool closed")


# Create FastAPI app
app = FastAPI(
    title="Zava Popup Store API",
    description="REST API for Zava popup clothing store",
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
        "service": "zava-api",
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


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Zava Popup Store API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "featured_products": "/api/products/featured",
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.api.app:app",
        host="0.0.0.0",
        port=8091,
        reload=True,
        log_level="info"
    )
