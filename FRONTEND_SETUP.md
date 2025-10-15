# Zava Popup Store - Frontend Setup Guide

## 📋 Overview

I've created a modern, responsive Vue.js frontend for the Zava popup clothing store. The frontend is designed to look realistic and professional while focusing on demonstrating the AI-powered procurement features in the backend.

## 🎨 What's Been Created

### Project Structure
```
frontend/
├── public/
│   └── images/
│       └── products/          # Product images (to be added)
├── src/
│   ├── assets/
│   │   └── main.css           # Global styles
│   ├── components/
│   │   ├── AppHeader.vue      # Navigation header with dropdowns
│   │   ├── AppFooter.vue      # Footer with links and newsletter
│   │   └── ProductCard.vue    # Reusable product card component
│   ├── views/
│   │   ├── HomePage.vue       # Landing page with featured products
│   │   ├── CategoryPage.vue   # Category/subcategory product listings
│   │   ├── ProductPage.vue    # Product detail page
│   │   └── StoresPage.vue     # Store locations page
│   ├── services/
│   │   └── api.js             # Axios-based API service
│   ├── config/
│   │   └── api.js             # API configuration (easy to change)
│   ├── router/
│   │   └── index.js           # Vue Router setup
│   ├── App.vue                # Root component
│   └── main.js                # Application entry point
├── .env                        # Environment variables
├── .env.example                # Environment template
├── index.html                  # HTML entry point
├── vite.config.js              # Vite configuration
├── package.json                # Dependencies
├── setup-node.sh               # Node.js installation script
└── README.md                   # Documentation
```

## ✨ Features Implemented

### 1. **Navigation Menu**
- Responsive header with dropdown menus
- Categories organized as specified:
  - Accessories (7 subcategories)
  - Bottoms (3 subcategories)
  - Tops (5 subcategories)
  - Footwear (4 subcategories)
  - Outerwear (2 subcategories)
- Mobile-friendly hamburger menu
- Sticky header for easy navigation

### 2. **Homepage**
- Hero section with call-to-action
- Category cards with product counts
- Featured products grid (fetches from API)
- Store locations banner
- Fully responsive design

### 3. **Category Pages**
- Product listings by category/subcategory
- Sort functionality (price, name, featured)
- Breadcrumb navigation
- Product count display
- Responsive grid layout

### 4. **Product Detail Page**
- Large product image display
- Product information and pricing
- Size selector (mock)
- Color selector (mock)
- Quantity controls
- Add to cart (mock)
- Add to wishlist (mock)
- Stock status
- Store availability link

### 5. **Store Locations Page**
- All 7 popup store locations from database
- Store hours and contact info
- Product count per store
- Get directions button (mock)

### 6. **Mock Features** (Placeholders)
- User login/signup
- Shopping cart
- Checkout process
- Search functionality
- Newsletter subscription
- Social media links

## 🔧 API Integration

The frontend is configured to fetch real data from your backend API at `http://localhost:8091/api`.

### Expected API Endpoints:
```
GET /api/categories                      - Get all categories
GET /api/products                        - Get all products
GET /api/products/category/:category     - Get products by category
GET /api/products/featured               - Get featured products
GET /api/products/:id                    - Get product by ID
```

### Easy Configuration:
The API base URL can be changed in two ways:

1. **Environment Variable** (recommended):
   ```bash
   # Edit frontend/.env
   VITE_API_BASE_URL=http://localhost:8091
   ```

2. **Direct Configuration**:
   ```javascript
   // Edit frontend/src/config/api.js
   const API_BASE_URL = 'http://localhost:8091';
   ```

### Fallback Behavior:
If the API is not available, the frontend automatically uses mock data based on your database documentation, so the UI remains functional for demos.

## 🚀 Installation & Setup

### Step 1: Install Node.js (if not already installed)

Run the provided setup script:
```bash
cd /workspace/frontend
./setup-node.sh
```

Or manually install Node.js:
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Step 2: Install Dependencies

```bash
cd /workspace/frontend
npm install
```

### Step 3: Start Development Server

```bash
npm run dev
```

The frontend will be available at: `http://localhost:3000`

### Step 4: Build for Production

```bash
npm run build
```

Built files will be in `frontend/dist/`

## 📸 Adding Product Images

1. Add product images to `frontend/public/images/products/`
2. Name them by product ID: `1.jpg`, `2.jpg`, `3.jpg`, etc.
3. Recommended specs:
   - Format: JPG or PNG
   - Dimensions: 800x1000px (3:4 aspect ratio)
   - File size: < 200KB

If images aren't found, a placeholder will be shown.

## 🎨 Design Features

- **Modern, Clean UI**: Professional design with Inter font family
- **Responsive**: Works on desktop, tablet, and mobile
- **Smooth Animations**: Hover effects, transitions, and loading states
- **Accessible**: Semantic HTML and ARIA labels
- **Color Scheme**: 
  - Primary: #1a1a1a (black)
  - Accent: #007bff (blue)
  - Clean, minimal color palette

## 📦 Product Data Format

The frontend expects product data in this format:
```javascript
{
  id: 1,                          // or product_id
  name: "Product Name",           // or product_name
  category: "Category Name",      // or category_name
  price: 79.99,                   // or unit_price
  originalPrice: 99.99,           // optional, for sale items
  badge: "New"                    // optional: "New", "Sale", "Popular"
}
```

## 🔄 Component Communication

- **Props**: Parent to child data flow
- **Events**: Child to parent communication
- **Router**: Page navigation
- **API Service**: Centralized data fetching

## 🎯 Next Steps

1. **Install Node.js**: Run `./setup-node.sh`
2. **Start Frontend**: Run `npm run dev`
3. **Create Backend API**: Implement the REST endpoints (or I can help with that!)
4. **Add Product Images**: Place images in `public/images/products/`
5. **Customize**: Adjust colors, styles, or content as needed

## 💡 Tips

- The frontend works standalone with mock data for quick demos
- All "Coming Soon" features alert the user - easy to extend
- API calls are logged to console for debugging
- Responsive design tested for mobile, tablet, and desktop
- Vue DevTools recommended for development

## 🛠️ Tech Stack

- **Vue 3** (Composition API ready, using Options API for simplicity)
- **Vue Router 4** - Client-side routing
- **Axios** - HTTP requests
- **Vite** - Fast build tool and dev server
- **Vanilla CSS** - No framework dependencies, easy to customize

## 📞 Need Help?

The code is well-commented and organized. Each component is self-contained and easy to understand. If you need any modifications or have questions, just ask!

---

**Note**: This is a demo frontend focused on showing a realistic retail interface. The real functionality demonstration is in your AI-powered procurement backend!
