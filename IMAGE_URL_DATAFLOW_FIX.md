# Image URL Data Flow Fix

## Problem
The `image_url` field from the API was not reaching the Vue.js components because the API response structure wasn't being properly parsed.

## Root Cause
The backend API returns:
```json
{
  "products": [
    {
      "product_id": 1,
      "product_name": "Example Product",
      "image_url": "example.png",
      ...
    }
  ],
  "total": 8
}
```

But the frontend code was treating the entire response as if it were the array directly:
```javascript
const data = await apiService.getFeaturedProducts(8);
if (Array.isArray(data)) { // This would fail!
```

## Solution

### 1. HomePage.vue (`/workspace/frontend/src/views/HomePage.vue`)
**Before:**
```javascript
const data = await apiService.getFeaturedProducts(8);
if (Array.isArray(data)) {
  this.featuredProducts = data.map(item => ({
    // missing image_url extraction
  }));
}
```

**After:**
```javascript
const response = await apiService.getFeaturedProducts(8);
const data = response.products || response;  // Extract products array
if (Array.isArray(data)) {
  this.featuredProducts = data.map(item => ({
    id: item.product_id || item.id,
    name: item.product_name || item.name,
    category: item.category_name || item.category,
    price: item.unit_price || item.price,
    originalPrice: item.original_price,
    badge: item.badge,
    image_url: item.image_url  // ✅ Now included
  }));
}
```

### 2. CategoryPage.vue (`/workspace/frontend/src/views/CategoryPage.vue`)
Applied the same fix to properly extract the products array and include `image_url`:

```javascript
const response = await apiService.getProductsByCategory(category);
const data = response.products || response;
if (Array.isArray(data)) {
  this.products = data.map(item => ({
    id: item.product_id || item.id,
    name: item.product_name || item.name,
    category: item.category_name || item.category,
    price: item.unit_price || item.price,
    originalPrice: item.original_price,
    badge: item.badge,
    image_url: item.image_url  // ✅ Now included
  }));
}
```

### 3. ProductCard.vue (Already Fixed)
The component was already set up to use `image_url`:
```javascript
productImageUrl() {
  if (this.imageError) {
    return config.placeholderImage;
  }
  if (this.product.image_url) {
    return this.product.image_url.startsWith('/') 
      ? this.product.image_url 
      : `/images/${this.product.image_url}`;
  }
  console.log("No image url");
  this.imageError = true;
}
```

## Data Flow (Complete)

1. **API Response** → `{products: [{...image_url...}], total: N}`
2. **API Service** → Returns raw response.data
3. **Page Components** → Extract `response.products` array
4. **Map/Transform** → Include `image_url` in mapped object
5. **ProductCard** → Receives product with `image_url` property
6. **Computed Property** → Prepends `/images/` to create full path
7. **Vite Middleware** → Serves image from `/workspace/images/`
8. **Browser** → Displays image

## Testing

### Verify API Response Structure:
```bash
curl -s 'http://localhost:8091/api/products/featured?limit=1' | jq '.products[0] | {name: .product_name, image: .image_url}'
```

Expected output:
```json
{
  "name": "Product Name",
  "image": "category_type_product_timestamp.png"
}
```

### Verify Frontend Data:
Open browser console and check:
```javascript
// Should show image_url property
console.log(this.featuredProducts[0])
```

## Files Modified
- ✅ `/workspace/frontend/src/views/HomePage.vue` - Fixed response parsing, added image_url
- ✅ `/workspace/frontend/src/views/CategoryPage.vue` - Fixed response parsing, added image_url  
- ✅ `/workspace/frontend/src/components/ProductCard.vue` - Already handles image_url correctly

## Result
✅ Product images now display correctly on:
- Homepage (featured products)
- Category pages (all products)
- Any page using the ProductCard component

The `image_url` field now flows correctly from the database → API → Vue components → DOM.
