# SQLAlchemy Async Migration Guide

## Overview
This document tracks the migration from raw PostgreSQL queries to SQLAlchemy async with SQLite backend.

## Setup Complete ✅

### 1. SQLAlchemy Models
Location: `/workspace/app/models/sqlite/`

All models are defined and ready to use:
- `Base` - Declarative base
- `Store`, `Product`, `Category`, `ProductType`
- `Inventory`, `Supplier`, `SupplierContract`
- `Order`, `OrderItem`, `Customer`
- `CompanyPolicy`, `Approver`, `Notification`
- `ProcurementRequest`, `SupplierPerformance`
- `ProductDescriptionEmbedding`, `ProductImageEmbedding`

### 2. Configuration
Added to `/workspace/app/config.py`:
```python
@property
def sqlite_database_url(self) -> str:
    """Returns the SQLite database URL."""
    return self._sqlite_database_url
```

Default: `sqlite+aiosqlite:///./data/retail.db`
Override with env var: `SQLITE_DATABASE_URL`

### 3. Lifespan Setup
Updated `/workspace/app/api/app.py`:

**Global Variables:**
```python
sqlalchemy_engine: Optional[AsyncEngine] = None
async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None
```

**Startup:**
- Creates async SQLAlchemy engine with aiosqlite driver
- Configures connection pool with:
  - 30 second timeout
  - `check_same_thread=False` for SQLite
  - `pool_pre_ping=True` for connection health checks
  - `echo=False` for quiet mode
- Creates async session factory with `expire_on_commit=False`

**Shutdown:**
- Properly disposes of the engine and all connections

### 4. Helper Function
```python
def get_db_session() -> AsyncSession:
    """
    Get a new SQLAlchemy async session.
    
    Usage:
        async with get_db_session() as session:
            result = await session.execute(select(Product))
            products = result.scalars().all()
    """
```

## Next Steps

### Phase 1: Convert Simple Endpoints
Start with endpoints that do simple queries:

1. **GET /api/categories** (already uses simple query)
2. **GET /api/stores** (single table, aggregations)
3. **GET /health** (update database status check)

### Phase 2: Convert Product Endpoints
More complex queries with joins:

1. **GET /api/products/featured**
2. **GET /api/products/category/{category}**
3. **GET /api/products/{product_id}**
4. **GET /api/products/sku/{sku}**

### Phase 3: Convert Management Endpoints
Most complex with multiple joins and aggregations:

1. **GET /api/management/dashboard/top-categories**
2. **GET /api/management/suppliers**
3. **GET /api/management/inventory**
4. **GET /api/management/products**

## Example Migration Pattern

### Before (Raw SQL):
```python
@app.get("/api/stores", response_model=StoreList)
async def get_stores() -> StoreList:
    if not db_provider:
        raise HTTPException(status_code=500, detail="Database not available")
    
    query = """
        SELECT s.store_id, s.store_name, ...
        FROM retail.stores s
        ...
    """
    async with db_provider.connection_pool.acquire() as conn:
        rows = await conn.fetch(query)
        ...
```

### After (SQLAlchemy):
```python
@app.get("/api/stores", response_model=StoreList)
async def get_stores() -> StoreList:
    async with get_db_session() as session:
        # Build query using SQLAlchemy ORM
        stmt = (
            select(
                Store.store_id,
                Store.store_name,
                Store.location,
                Store.is_online,
                Store.location_key,
                func.count(Inventory.product_id).label("products"),
                func.sum(Inventory.stock_level).label("total_stock"),
                ...
            )
            .select_from(Store)
            .outerjoin(Inventory, Store.store_id == Inventory.store_id)
            .outerjoin(Product, Inventory.product_id == Product.product_id)
            .group_by(Store.store_id)
            .order_by(Store.store_name)
        )
        
        result = await session.execute(stmt)
        rows = result.all()
        
        stores = [
            Store(
                id=row.store_id,
                name=row.store_name,
                ...
            )
            for row in rows
        ]
        
        return StoreList(stores=stores, total=len(stores))
```

## Key Patterns

### Session Management
Always use async context manager:
```python
async with get_db_session() as session:
    # Your queries here
    # Session automatically commits on success
    # Rolls back on exception
```

### Query Construction
```python
from sqlalchemy import select, func, and_, or_

# Simple select
stmt = select(Product).where(Product.product_id == product_id)

# With joins
stmt = (
    select(Product, Category)
    .join(Category, Product.category_id == Category.category_id)
)

# With aggregations
stmt = (
    select(
        Category.category_name,
        func.count(Product.product_id).label("count")
    )
    .group_by(Category.category_name)
)
```

### Executing Queries
```python
# Single result
result = await session.execute(stmt)
obj = result.scalar_one_or_none()

# Multiple results
result = await session.execute(stmt)
objects = result.scalars().all()

# With relationships loaded
from sqlalchemy.orm import selectinload
stmt = select(Store).options(selectinload(Store.inventory))
```

## Benefits

1. **Type Safety** - ORM provides type checking
2. **SQL Injection Protection** - Parameterized queries by default
3. **Portable** - Easy to switch databases (SQLite → PostgreSQL)
4. **Relationships** - ORM handles joins automatically
5. **Testing** - Easy to use in-memory SQLite for tests
6. **Maintainability** - Less string concatenation

## Dependencies

Already installed in requirements.lock.txt:
- `sqlalchemy` - ORM and query builder
- `aiosqlite` - Async SQLite driver
- `asyncpg` - Async PostgreSQL driver (if needed later)

## Testing

The pytest infrastructure is ready in `/workspace/tests/`:
- Use SQLite in-memory database: `sqlite+aiosqlite:///:memory:`
- Create test fixtures that populate database
- Each test gets fresh database instance

Example test fixture:
```python
@pytest.fixture
async def test_db_session():
    """Create a test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()
```

## Notes

- PostgreSQL connection pool (`db_provider`) still active during migration
- Can migrate endpoints incrementally
- Both database backends can coexist temporarily
- Remove PostgreSQL code once migration complete
