#!/usr/bin/env python3
"""
FastAPI Backend for GitHub Popup Store
Provides REST API endpoints for the frontend application.
"""

import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from agent_framework import (ChatMessage,
                             ExecutorInvokedEvent,
                             ExecutorCompletedEvent,
                             ExecutorFailedEvent,
                             WorkflowOutputEvent,
                             WorkflowStartedEvent)
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
# Initialize in startup event
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

from pydantic import BaseModel, Field
import json
from datetime import datetime, timezone
from app.config import Config
from app.agents.stock import workflow

# SQLAlchemy imports for SQLite
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.models.sqlite import Base
from app.models.sqlite.stores import Store as StoreModel
from app.models.sqlite.inventory import Inventory as InventoryModel
from app.models.sqlite.products import Product as ProductModel
from app.models.sqlite.categories import Category as CategoryModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
config = Config()
SCHEMA_NAME = "retail"

# Database connections
sqlalchemy_engine: Optional[AsyncEngine] = None
async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


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


class Store(BaseModel):
    """Store location model for API responses"""
    id: int = Field(..., description="Unique store identifier")
    name: str = Field(..., description="Store name")
    location: str = Field(..., description="Store location/address")
    is_online: bool = Field(..., description="Whether this is an online store")
    location_key: str = Field(..., description="Location key for image mapping")
    products: int = Field(..., description="Number of products in stock")
    total_stock: int = Field(..., description="Total stock level across products")
    inventory_value: float = Field(..., description="Total inventory retail value")
    status: str = Field(..., description="Store status (Open/Online)")
    hours: str = Field(..., description="Store operating hours")


class StoreList(BaseModel):
    """List of stores response"""
    stores: List[Store]
    total: int


class Category(BaseModel):
    """Category model for API responses"""
    id: int = Field(..., description="Unique category identifier")
    name: str = Field(..., description="Category name")


class CategoryList(BaseModel):
    """List of categories response"""
    categories: List[Category]
    total: int


class TopCategory(BaseModel):
    """Top category model for dashboard analytics"""
    name: str = Field(..., description="Category name")
    revenue: float = Field(..., description="Total retail value of inventory")
    percentage: float = Field(..., description="Percentage relative to top category")
    product_count: int = Field(..., description="Number of distinct products")
    total_stock: int = Field(..., description="Total stock level across products")
    cost_value: float = Field(..., description="Total cost value of inventory")
    potential_profit: float = Field(..., description="Potential profit if all sold")


class TopCategoryList(BaseModel):
    """List of top categories response"""
    categories: List[TopCategory]
    total: int = Field(..., description="Number of categories returned")
    max_value: float = Field(..., description="Maximum revenue value for percentage calculation")


class Supplier(BaseModel):
    """Supplier model for management interface"""
    id: int = Field(..., description="Unique supplier identifier")
    name: str = Field(..., description="Supplier name")
    code: str = Field(..., description="Supplier code")
    location: str = Field(..., description="Supplier location (city, state)")
    contact: str = Field(..., description="Contact email address")
    phone: str = Field(..., description="Contact phone number")
    rating: float = Field(..., description="Supplier rating (0.0 to 5.0)")
    esg_compliant: bool = Field(..., description="ESG compliance status")
    approved: bool = Field(..., description="Approved vendor status")
    preferred: bool = Field(..., description="Preferred vendor status")
    categories: List[str] = Field(..., description="Product categories supplied")
    lead_time: int = Field(..., description="Lead time in days")
    payment_terms: str = Field(..., description="Payment terms")
    min_order: float = Field(..., description="Minimum order amount")
    bulk_discount: float = Field(..., description="Bulk discount percentage")


class SupplierList(BaseModel):
    """List of suppliers response"""
    suppliers: List[Supplier]
    total: int = Field(..., description="Total number of suppliers")


class InventoryItem(BaseModel):
    """Inventory item model for management interface"""
    store_id: int = Field(..., description="Store identifier")
    store_name: str = Field(..., description="Store name")
    store_location: str = Field(..., description="Store location description")
    is_online: bool = Field(..., description="Whether this is an online store")
    product_id: int = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name")
    sku: str = Field(..., description="Product SKU")
    category: str = Field(..., description="Product category")
    type: str = Field(..., description="Product type")
    stock_level: int = Field(..., description="Current stock level")
    reorder_point: int = Field(..., description="Reorder threshold")
    is_low_stock: bool = Field(..., description="Whether stock is below reorder point")
    unit_cost: float = Field(..., description="Unit cost")
    unit_price: float = Field(..., description="Unit retail price")
    stock_value: float = Field(..., description="Total cost value of stock")
    retail_value: float = Field(..., description="Total retail value of stock")
    supplier_name: Optional[str] = Field(None, description="Supplier name")
    supplier_code: Optional[str] = Field(None, description="Supplier code")
    lead_time: Optional[int] = Field(None, description="Lead time in days")
    image_url: Optional[str] = Field(None, description="Product image URL")


class InventorySummary(BaseModel):
    """Inventory summary statistics"""
    total_items: int = Field(..., description="Total number of inventory items")
    low_stock_count: int = Field(..., description="Number of low stock items")
    total_stock_value: float = Field(..., description="Total cost value of all stock")
    total_retail_value: float = Field(..., description="Total retail value of all stock")
    avg_stock_level: float = Field(..., description="Average stock level per item")


class InventoryResponse(BaseModel):
    """Inventory response with items and summary"""
    inventory: List[InventoryItem]
    summary: InventorySummary


class ManagementProduct(BaseModel):
    """Model for product information in management interface with inventory details."""
    product_id: int = Field(..., description="Unique product identifier")
    sku: str = Field(..., description="Stock Keeping Unit identifier")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    category: str = Field(..., description="Product category name")
    type: str = Field(..., description="Product type name")
    base_price: float = Field(..., description="Base retail price")
    cost: float = Field(..., description="Cost per unit")
    margin: float = Field(..., description="Gross margin percentage")
    discontinued: bool = Field(..., description="Whether product is discontinued")
    supplier_id: Optional[int] = Field(None, description="Supplier identifier")
    supplier_name: Optional[str] = Field(None, description="Supplier name")
    supplier_code: Optional[str] = Field(None, description="Supplier code")
    lead_time: Optional[int] = Field(None, description="Lead time in days")
    total_stock: int = Field(..., description="Total stock across all stores")
    store_count: int = Field(..., description="Number of stores carrying this product")
    stock_value: float = Field(..., description="Total inventory value at cost")
    retail_value: float = Field(..., description="Total inventory value at retail price")
    image_url: Optional[str] = Field(None, description="Product image URL")


class ProductPagination(BaseModel):
    """Pagination information for product list."""
    total: int = Field(..., description="Total number of products matching criteria")
    limit: int = Field(..., description="Maximum number of products per page")
    offset: int = Field(..., description="Current offset in results")
    has_more: bool = Field(..., description="Whether more products are available")


class ManagementProductResponse(BaseModel):
    """Response model for management products list with pagination."""
    products: List[ManagementProduct] = Field(..., description="List of products")
    pagination: ProductPagination = Field(..., description="Pagination information")


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown events"""
    global sqlalchemy_engine, async_session_factory

    # Startup
    logger.info("🚀 Starting GitHub API Server...")

    # Initialize SQLAlchemy async engine for SQLite
    try:
        sqlite_url = config.sqlite_database_url or "sqlite+aiosqlite:///./data/retail.db"
        sqlalchemy_engine = create_async_engine(
            sqlite_url,
            connect_args={"timeout": 30, "check_same_thread": False},
            pool_pre_ping=True,
            echo=False,
        )

        # Create async session factory
        async_session_factory = async_sessionmaker(
            sqlalchemy_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        logger.info(f"✅ SQLAlchemy async engine created: {sqlite_url}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize SQLAlchemy: {e}")
        raise

    # Initialize cache
    backend = InMemoryBackend()
    FastAPICache.init(backend=backend)

    yield

    # Shutdown
    logger.info("🛑 Shutting down GitHub API Server...")

    # Dispose SQLAlchemy engine
    if sqlalchemy_engine:
        await sqlalchemy_engine.dispose()
        logger.info("✅ SQLAlchemy async engine disposed")


# Create FastAPI app
app = FastAPI(
    title="GitHub Popup Store API",
    description="REST API for GitHub popup merchandise store",
    version="1.0.0",
    lifespan=lifespan
)


# Helper function to get SQLAlchemy session
def get_db_session() -> AsyncSession:
    """
    Get a new SQLAlchemy async session.

    Returns:
        AsyncSession: A new async database session

    Raises:
        RuntimeError: If the session factory is not initialized
    """
    if not async_session_factory:
        raise RuntimeError(
            "Database session factory not initialized. "
            "Ensure the application has started."
        )
    return async_session_factory()


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


# Stores endpoint
@app.get("/api/stores", response_model=StoreList)
@cache(expire=600)
async def get_stores() -> StoreList:
    """
    Get all store locations with inventory counts and details.
    Returns comprehensive store information for the stores page.
    """
    try:
        async with get_db_session() as session:
            # Build SQLAlchemy query with aggregations
            stmt = (
                select(
                    StoreModel.store_id,
                    StoreModel.store_name,
                    StoreModel.is_online,
                    func.count(func.distinct(InventoryModel.product_id)).label(
                        "product_count"
                    ),
                    func.sum(InventoryModel.stock_level).label("total_stock"),
                    func.sum(
                        InventoryModel.stock_level * ProductModel.cost
                    ).label("inventory_cost_value"),
                    func.sum(
                        InventoryModel.stock_level * ProductModel.base_price
                    ).label("inventory_retail_value"),
                )
                .select_from(StoreModel)
                .outerjoin(
                    InventoryModel,
                    StoreModel.store_id == InventoryModel.store_id
                )
                .outerjoin(
                    ProductModel,
                    InventoryModel.product_id == ProductModel.product_id
                )
                .group_by(
                    StoreModel.store_id,
                    StoreModel.store_name,
                    StoreModel.is_online
                )
                .order_by(StoreModel.is_online.asc(), StoreModel.store_name)
            )

            result = await session.execute(stmt)
            rows = result.all()

            stores: list[Store] = []
            for row in rows:
                store_name = row.store_name

                # Extract location key for images
                if row.is_online:
                    location_key = "online"
                    location = "Online Warehouse, Seattle, WA"
                else:
                    # Extract location from "GitHub Popup Location" format
                    parts = store_name.split('Popup ')
                    if len(parts) > 1:
                        location_name = parts[1]
                        location_key = location_name.lower().replace(' ', '_')
                        # Format address from location name
                        location = location_name
                    else:
                        location_key = store_name.lower().replace(' ', '_')
                        location = "Washington State"

                stores.append(Store(
                    id=row.store_id,
                    name=store_name,
                    location=location,
                    is_online=row.is_online,
                    location_key=location_key,
                    products=int(row.product_count or 0),
                    total_stock=int(row.total_stock or 0),
                    inventory_value=round(
                        float(row.inventory_retail_value or 0), 2
                    ),
                    status="Online" if row.is_online else "Open",
                    hours=(
                        "24/7 Online" if row.is_online
                        else "Mon-Sun: 10am-7pm"
                    )
                ))

            logger.info(f"✅ Retrieved {len(stores)} stores")

            return StoreList(stores=stores, total=len(stores))

    except Exception as e:
        logger.error(f"❌ Error fetching stores: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch stores: {str(e)}"
        )


# Categories endpoint
@app.get("/api/categories", response_model=CategoryList)
@cache(expire=3600)
async def get_categories() -> CategoryList:
    """
    Get all product categories.
    Returns a list of all available categories in the system.
    """
    try:
        async with get_db_session() as session:
            # Build SQLAlchemy query for categories
            stmt = (
                select(
                    CategoryModel.category_id,
                    CategoryModel.category_name
                )
                .order_by(CategoryModel.category_name)
            )

            result = await session.execute(stmt)
            rows = result.all()

            categories: list[Category] = []
            for row in rows:
                categories.append(Category(
                    id=row.category_id,
                    name=row.category_name
                ))

            logger.info(f"✅ Retrieved {len(categories)} categories")

            return CategoryList(categories=categories, total=len(categories))

    except Exception as e:
        logger.error(f"❌ Error fetching categories: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch categories: {str(e)}"
        )


# Featured products endpoint
@app.get("/api/products/featured", response_model=ProductList)
@cache(expire=600)
async def get_featured_products(
    limit: int = Query(8, ge=1, le=50, description="Number of products to return")
) -> ProductList:
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
) -> ProductList:
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
            # Get total products in category for pagination
            total_query = """
                SELECT COUNT(*) FROM retail.products p
                INNER JOIN retail.categories c ON p.category_id = c.category_id
                WHERE p.discontinued = false
                    AND LOWER(c.category_name) = LOWER($1)
            """
            total_count: int = await conn.fetchval(total_query, category) # pyright: ignore[reportAssignmentType]
            if total_count == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"No products found in category '{category}'"
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
                total=total_count
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
async def get_product_by_id(product_id: int) -> Product:
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


@app.get("/api/products/sku/{sku}", response_model=Product)
async def get_product_by_sku(sku: str) -> Product:
    """
    Get a single product by its SKU.
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
            # Query single product by SKU
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
                    s.contact_email as supplier_email,
                    s.contact_phone as supplier_phone,
                    p.discontinued,
                    pie.image_url
                FROM retail.products p
                INNER JOIN retail.categories c ON p.category_id = c.category_id
                INNER JOIN retail.product_types pt ON p.type_id = pt.type_id
                LEFT JOIN retail.suppliers s ON p.supplier_id = s.supplier_id
                LEFT JOIN retail.product_image_embeddings pie ON p.product_id = pie.product_id
                WHERE p.sku = $1
            """

            row = await conn.fetchrow(query, sku)

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with SKU '{sku}' not found"
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

            logger.info(f"✅ Retrieved product by SKU {sku}: {product.product_name}")

            return product

        finally:
            await db_provider.release_connection(conn)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching product by SKU {sku}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch product: {str(e)}"
        )


@app.get("/api/management/dashboard/top-categories", response_model=TopCategoryList)
@cache(expire=600)
async def get_top_categories(limit: int = Query(5, ge=1, le=10, description="Number of top categories to return")) -> TopCategoryList:
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
                return TopCategoryList(
                    categories=[],
                    total=0,
                    max_value=0.0
                )

            # Calculate max value for percentage calculation
            max_value = float(rows[0]['total_retail_value']) if rows else 0
            
            categories: list[TopCategory] = []
            for row in rows:
                retail_value = float(row['total_retail_value'])
                percentage = round((retail_value / max_value * 100), 1) if max_value > 0 else 0
                
                categories.append(TopCategory(
                    name=row['category_name'],
                    revenue=round(retail_value, 2),
                    percentage=percentage,
                    product_count=int(row['product_count']),
                    total_stock=int(row['total_stock']),
                    cost_value=round(float(row['total_cost_value']), 2),
                    potential_profit=round(float(row['potential_profit']), 2)
                ))

            logger.info(f"✅ Retrieved {len(categories)} categories")

            return TopCategoryList(
                categories=categories,
                total=len(categories),
                max_value=round(max_value, 2)
            )

        finally:
            await db_provider.release_connection(conn)

    except Exception as e:
        logger.error(f"❌ Error fetching top categories: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch top categories: {str(e)}"
        )


@app.get("/api/management/suppliers", response_model=SupplierList)
async def get_suppliers() -> SupplierList:
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

            suppliers: list[Supplier] = []
            for row in rows:
                # Format location
                location = (
                    f"{row['city']}, {row['state_province']}"
                    if row['city'] else "N/A"
                )
                
                suppliers.append(Supplier(
                    id=row['supplier_id'],
                    name=row['supplier_name'],
                    code=row['supplier_code'],
                    location=location,
                    contact=row['contact_email'],
                    phone=row['contact_phone'] or "N/A",
                    rating=float(row['supplier_rating']) if row['supplier_rating'] else 0.0,
                    esg_compliant=row['esg_compliant'],
                    approved=row['approved_vendor'],
                    preferred=row['preferred_vendor'],
                    categories=row['categories'] or [],
                    lead_time=row['lead_time_days'],
                    payment_terms=row['payment_terms'],
                    min_order=float(row['minimum_order_amount']) if row['minimum_order_amount'] else 0.0,
                    bulk_discount=float(row['bulk_discount_percent']) if row['bulk_discount_percent'] else 0.0
                ))

            logger.info(f"✅ Retrieved {len(suppliers)} suppliers")

            return SupplierList(
                suppliers=suppliers,
                total=len(suppliers)
            )

        finally:
            await db_provider.release_connection(conn)

    except Exception as e:
        logger.error(f"❌ Error fetching suppliers: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch suppliers: {str(e)}"
        )


@app.get("/api/management/inventory", response_model=InventoryResponse)
async def get_inventory(
    store_id: Optional[int] = None,
    product_id: Optional[int] = None,
    category: Optional[str] = None,
    low_stock_only: bool = False,
    low_stock_threshold: int = 10,
    limit: int = 100
) -> InventoryResponse:
    """
    Get inventory levels across stores with product and category details.
    
    Args:
        store_id: Optional filter by specific store
        product_id: Optional filter by specific product
        category: Optional filter by product category
        low_stock_only: Show only items with stock below reorder threshold
        low_stock_threshold: Threshold for considering stock as low (default: 10)
        limit: Maximum number of records to return
    """
    conn = await db_provider.get_connection()
    
    try:
        logger.info(f"📦 Fetching inventory (store={store_id}, product={product_id}, category={category}, low_stock={low_stock_only})...")

        # Build dynamic WHERE clause and filter params
        where_conditions = []
        filter_params = []
        param_idx = 1

        if store_id is not None:
            where_conditions.append(f"st.store_id = ${param_idx}")
            filter_params.append(store_id)
            param_idx += 1

        if product_id is not None:
            where_conditions.append(f"p.product_id = ${param_idx}")
            filter_params.append(product_id)
            param_idx += 1

        if category:
            where_conditions.append(f"LOWER(c.category_name) = LOWER(${param_idx})")
            filter_params.append(category)
            param_idx += 1

        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        # First, get summary statistics for ALL matching records (not limited)
        # Note: Count distinct products, not inventory records (product x store combinations)
        threshold_param_idx = param_idx  # Store the index for threshold
        summary_query = f"""
            SELECT
                COUNT(DISTINCT p.product_id) as total_items,
                SUM(CASE WHEN i.stock_level < ${threshold_param_idx} THEN 1 ELSE 0 END) as low_stock_count,
                SUM(i.stock_level * p.cost) as total_stock_value,
                SUM(i.stock_level * p.base_price) as total_retail_value,
                AVG(i.stock_level) as avg_stock_level
            FROM retail.inventory i
            INNER JOIN retail.stores st ON i.store_id = st.store_id
            INNER JOIN retail.products p ON i.product_id = p.product_id
            INNER JOIN retail.categories c ON p.category_id = c.category_id
            INNER JOIN retail.product_types pt ON p.type_id = pt.type_id
            {where_clause}
        """
        
        # Execute summary query with filter params + threshold
        summary_params = filter_params + [low_stock_threshold]
        summary_row = await conn.fetchrow(summary_query, *summary_params)
        
        # Now get the limited result set for display
        limit_param_idx = param_idx  # Same index position for limit (separate query)
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
            LIMIT ${limit_param_idx}
        """

        # Execute main query with filter params + limit
        query_params = filter_params + [limit]
        rows = await conn.fetch(query, *query_params)

        inventory_items: list[InventoryItem] = []
        for row in rows:
            stock_level = row['stock_level']
            # Use the threshold parameter for reorder point
            # In production, this would come from a products or inventory_settings table
            reorder_point = low_stock_threshold
            
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
            
            inventory_items.append(InventoryItem(
                store_id=row['store_id'],
                store_name=row['store_name'],
                store_location=store_location,
                is_online=row['is_online'],
                product_id=row['product_id'],
                product_name=row['product_name'],
                sku=row['sku'],
                category=row['category_name'],
                type=row['type_name'],
                stock_level=stock_level,
                reorder_point=reorder_point,
                is_low_stock=is_low_stock,
                unit_cost=float(row['cost']) if row['cost'] else 0,
                unit_price=float(row['base_price']) if row['base_price'] else 0,
                stock_value=round(stock_value, 2),
                retail_value=round(retail_value, 2),
                supplier_name=row['supplier_name'],
                supplier_code=row['supplier_code'],
                lead_time=row['lead_time_days'],
                image_url=row['image_url']
            ))

        # Use the summary statistics from the dedicated query (all records, not limited)
        total_items = int(summary_row['total_items']) if summary_row['total_items'] else 0
        low_stock_count = int(summary_row['low_stock_count']) if summary_row['low_stock_count'] else 0
        total_stock_value = float(summary_row['total_stock_value']) if summary_row['total_stock_value'] else 0.0
        total_retail_value = float(summary_row['total_retail_value']) if summary_row['total_retail_value'] else 0.0
        avg_stock = float(summary_row['avg_stock_level']) if summary_row['avg_stock_level'] else 0.0

        logger.info(f"✅ Retrieved {len(inventory_items)} inventory items (showing {len(inventory_items)} of {total_items} total, {low_stock_count} low stock)")

        return InventoryResponse(
            inventory=inventory_items,
            summary=InventorySummary(
                total_items=total_items,
                low_stock_count=low_stock_count,
                total_stock_value=round(total_stock_value, 2),
                total_retail_value=round(total_retail_value, 2),
                avg_stock_level=round(avg_stock, 1)
            )
        )

    except Exception as e:
        logger.error(f"❌ Error fetching inventory: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch inventory: {str(e)}"
        )
    finally:
        await db_provider.release_connection(conn)


@app.get("/api/management/products", response_model=ManagementProductResponse)
async def get_products(
    category: Optional[str] = None,
    supplier_id: Optional[int] = None,
    discontinued: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> ManagementProductResponse:
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
            
            products.append(ManagementProduct(
                product_id=row['product_id'],
                sku=row['sku'],
                name=row['product_name'],
                description=row['product_description'],
                category=row['category_name'],
                type=row['type_name'],
                base_price=base_price,
                cost=cost,
                margin=margin,
                discontinued=row['discontinued'],
                supplier_id=row['supplier_id'],
                supplier_name=row['supplier_name'],
                supplier_code=row['supplier_code'],
                lead_time=row['lead_time_days'],
                total_stock=total_stock,
                store_count=int(row['store_count']),
                stock_value=round(stock_value, 2),
                retail_value=round(retail_value, 2),
                image_url=row['image_url']
            ))

        logger.info(f"✅ Retrieved {len(products)} products (total: {total_count})")

        return ManagementProductResponse(
            products=products,
            pagination=ProductPagination(
                total=total_count,
                limit=limit,
                offset=offset,
                has_more=(offset + len(products)) < total_count
            )
        )

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

        input_message = request_data.get('message', 'Analyze inventory and recommend restocking priorities')
        store_id = request_data.get('store_id')
        
        logger.info(f"🤖 AI Agent request: {input_message} (store_id: {store_id})")

        # Send initial acknowledgment
        await websocket.send_json({
            "type": "started",
            "message": "AI Agent workflow initiated...",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Run the workflow and stream events
        # Add store_id to the message if provided
        if store_id:
            full_message = f"{input_message}\n\nStore ID: {store_id}"
        else:
            full_message = input_message
            
        input: ChatMessage = ChatMessage(role='user', text=full_message)

        workflow_output = None
        try:
            async for event in workflow.run_stream(input):
                now = datetime.now(timezone.utc).isoformat()
                if isinstance(event, WorkflowStartedEvent):
                    event_data = {
                        "type": "workflow_started",
                        "event": str(event.data),
                        "timestamp": now
                    }
                elif isinstance(event, WorkflowOutputEvent):
                    # Capture the workflow output (markdown result)
                    if isinstance(event.data, BaseModel):
                        workflow_output = event.data.model_dump()
                    else:
                        workflow_output = str(event.data)
                    event_data = {
                        "type": "workflow_output",
                        "event": workflow_output,
                        "timestamp": now
                    }
                elif isinstance(event, ExecutorInvokedEvent):
                    event_data = {
                        "type": "step_started",
                        "event": event.data,
                        "id": event.executor_id,
                        "timestamp": now
                    }
                elif isinstance(event, ExecutorCompletedEvent):
                    event_data = {
                        "type": "step_completed",
                        "event": event.data,
                        "id": event.executor_id,
                        "timestamp": now
                    }
                elif isinstance(event, ExecutorFailedEvent):
                    event_data = {
                        "type": "step_failed",
                        "event": event.details.message,
                        "id": event.executor_id,
                        "timestamp": now
                    }
                else:
                    # Stream each workflow event to the frontend
                    event_data = {
                        "type": "event",
                        "event": str(event),
                        "timestamp": now
                    }
                await websocket.send_json(event_data)
                logger.info(f"📤 Sent event: {event}")

            # Send completion message with the workflow output
            await websocket.send_json({
                "type": "completed",
                "message": "Workflow completed successfully",
                "output": workflow_output,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            logger.info("✅ AI Agent workflow completed")

        except Exception as workflow_error:
            logger.error(f"❌ Workflow error: {workflow_error}")
            await websocket.send_json({
                "type": "error",
                "message": f"Workflow error: {str(workflow_error)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
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
@cache(expire=600)
async def root():
    """Root endpoint"""
    return {
        "service": "GitHub Popup Store API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "stores": "/api/stores",
            "categories": "/api/categories",
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
