# Zava API Backend - Quick Start Guide

## ✅ What's Implemented

### FastAPI Backend (`/workspace/app/api/app.py`)
A production-ready REST API server for the Zava popup store frontend.

#### Features:
- **FastAPI** with async/await support
- **CORS** configured for frontend (localhost:3000)
- **PostgreSQL** connection pooling using existing database functions
- **Pydantic** models for type safety and validation
- **Health check** endpoint
- **Featured products** endpoint with real database data

---

## 🎯 API Endpoints

### 1. Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "zava-api",
  "database": "connected"
}
```

### 2. Featured Products
```bash
GET /api/products/featured?limit=8
```

**Query Parameters:**
- `limit` (optional): Number of products to return (1-50, default: 8)

**Response:**
```json
{
  "products": [
    {
      "product_id": 28,
      "sku": "APP-SW-001",
      "product_name": "Crewneck Sweatshirt",
      "category_name": "Apparel - Tops",
      "type_name": "Sweatshirts",
      "unit_price": 44.76,
      "cost": 29.99,
      "gross_margin_percent": 33.0,
      "product_description": "Classic crewneck sweatshirt...",
      "supplier_name": "Formal Wear Specialists",
      "discontinued": false
    }
  ],
  "total": 8
}
```

### 3. Root Endpoint
```bash
GET /
```

Returns API information and available endpoints.

---

## 🚀 Running the API Server

### Method 1: Direct Python
```bash
cd /workspace
python -m app.api.app
```

The server will start on `http://0.0.0.0:8091`

### Method 2: Background Process
```bash
cd /workspace
python -m app.api.app > /tmp/api.log 2>&1 &
```

### Method 3: Using uvicorn directly
```bash
cd /workspace
uvicorn app.api.app:app --host 0.0.0.0 --port 8091 --reload
```

---

## 🧪 Testing the API

### Test with curl
```bash
# Health check
curl http://localhost:8091/health

# Get 5 featured products
curl http://localhost:8091/api/products/featured?limit=5

# Pretty print with jq (if installed)
curl -s http://localhost:8091/api/products/featured | jq .
```

### Test with Python
```python
import requests

# Health check
response = requests.get("http://localhost:8091/health")
print(response.json())

# Featured products
response = requests.get("http://localhost:8091/api/products/featured?limit=5")
products = response.json()
print(f"Got {products['total']} products")
```

### Test in Browser
Open: `http://localhost:8091/docs`

FastAPI automatically generates interactive API documentation (Swagger UI).

---

## 🔗 Connecting Frontend to Backend

The frontend is already configured to use the API:

1. **Start the API server** (port 8091):
   ```bash
   cd /workspace
   python -m app.api.app
   ```

2. **Start the frontend** (port 3000):
   ```bash
   cd /workspace/frontend
   npm run dev
   ```

3. **Visit the homepage**: `http://localhost:3000`

The featured products section will now load real data from the database!

---

## 📊 How It Works

### Database Connection
- Uses existing `PostgreSQLSchemaProvider` from `app/sales_analysis_postgres.py`
- Connection pooling for performance (1-3 connections)
- Async operations for scalability
- Automatic connection cleanup on shutdown

### Featured Products Query
```sql
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
```

**Strategy:**
- Exclude discontinued products
- Prefer products with higher profit margins
- Add randomness for variety
- Join categories and suppliers for complete data

---

## 🔧 Configuration

### CORS Origins (Configured)
- `http://localhost:3000` (frontend dev server)
- `http://127.0.0.1:3000`
- `http://localhost:5173` (Vite default)
- `http://127.0.0.1:5173`

### Database Connection
Uses environment variables from `.env`:
- `POSTGRES_DB_HOST`
- `POSTGRES_DB_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

Already configured by your Azure deployment!

---

## 📝 Next Steps

### Ready to Implement:
1. **Get all products** - `/api/products`
2. **Get products by category** - `/api/products/category/{category}`
3. **Get product by ID** - `/api/products/{id}`
4. **Get categories** - `/api/categories`
5. **Get stores** - `/api/stores`

### Management API:
6. **Dashboard stats** - `/api/management/dashboard`
7. **Suppliers** - `/api/management/suppliers`
8. **Inventory** - `/api/management/inventory`
9. **Products CRUD** - `/api/management/products`

---

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8091 is in use
lsof -i :8091

# Kill existing process
pkill -f "app.api.app"
```

### Database connection fails
```bash
# Check environment variables
env | grep POSTGRES

# Test database connection
python -c "from app.config import Config; c = Config(); print(c.postgres_url)"
```

### CORS errors in frontend
- Make sure frontend is running on port 3000
- Check browser console for specific error
- Verify API server CORS configuration

---

## ✨ Key Features

✅ **Production-ready** - Proper error handling and logging
✅ **Type-safe** - Pydantic models for validation
✅ **Async** - Non-blocking operations
✅ **Connection pooling** - Efficient database usage
✅ **Auto-reload** - Development mode with hot reload
✅ **Interactive docs** - Swagger UI at `/docs`
✅ **Health checks** - Monitor service status

---

**Ready to go!** The API is serving real data from your PostgreSQL database. 🚀
