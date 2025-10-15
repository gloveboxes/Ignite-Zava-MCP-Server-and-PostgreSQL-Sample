# Zava Frontend - Quick Start Checklist

## ✅ Step-by-Step Setup

### 1. Rebuild DevContainer
- [ ] Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
- [ ] Type: "Dev Containers: Rebuild Container"
- [ ] Wait for rebuild to complete (~5-10 minutes)

### 2. Verify Installation
After rebuild completes, verify in terminal:
```bash
node --version    # Should show v20.x.x
npm --version     # Should show 10.x.x
```

### 3. Navigate to Frontend
```bash
cd /workspace/frontend
```

### 4. Start Development Server
```bash
npm run dev
```

**You should see:**
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:3000/
➜  Network: http://172.x.x.x:3000/
```

### 5. Access the Frontend

**Important for DevContainer:**

✅ **Recommended:** Use VS Code port forwarding:
1. Look for VS Code notification: "Your application running on port 3000 is available"
2. Click "Open in Browser"

✅ **Or:** Use the Ports tab:
1. Click "PORTS" tab at bottom of VS Code
2. Find port 3000
3. Click the globe 🌐 icon

❌ **Don't:** Try to open `http://localhost:3000` directly in your browser
   (It won't work from outside the container without port forwarding)

## 📦 What You'll See

### Homepage
- Hero section with "Welcome to ZAVA"
- Category cards (Accessories, Bottoms, Tops, Footwear, Outerwear)
- Featured products grid
- Store locations banner

### Navigation
- Dropdown menus for all categories and subcategories
- Responsive mobile menu
- Cart icon (placeholder)
- Search icon (placeholder)

### Working Features
✅ Browse categories and subcategories
✅ View product listings
✅ Click on products to see details
✅ View store locations
✅ Responsive design (try resizing browser)

### Mock/Placeholder Features
- Login/Signup
- Shopping cart
- Checkout
- Search
- Newsletter signup

## 🔧 Configuration

### API Endpoint (Easy to Change)
Edit: `/workspace/frontend/.env`
```bash
VITE_API_BASE_URL=http://localhost:8091
```

### Mock Data
If backend API is not running, the frontend automatically uses mock data based on your database documentation.

## 🎨 Adding Product Images

1. Place images in: `/workspace/frontend/public/images/products/`
2. Name them by product ID: `1.jpg`, `2.jpg`, `3.jpg`, etc.
3. Recommended: 800x1000px, JPG format, <200KB

## 🚀 Building for Production

```bash
cd /workspace/frontend
npm run build
```

Output will be in: `/workspace/frontend/dist/`

## 📚 Documentation

- Full setup guide: `/workspace/FRONTEND_SETUP.md`
- DevContainer rebuild: `/workspace/DEVCONTAINER_REBUILD.md`
- Frontend README: `/workspace/frontend/README.md`

## 🐛 Troubleshooting

### Port already in use:
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
npm run dev
```

### Dependencies not installed:
```bash
cd /workspace/frontend
rm -rf node_modules
npm install
```

### API not connecting:
- Frontend works with mock data if API is unavailable
- Check API URL in `.env` file
- Check network tab in browser DevTools

## 💡 Tips

- Open browser DevTools Console to see API calls
- Vue DevTools extension recommended
- Hot reload is enabled - changes auto-refresh
- Mock data matches your database documentation

## 🎯 What's Next?

1. ✅ Rebuild devcontainer (includes Node.js)
2. ✅ Start frontend (`npm run dev`)
3. ⏭️ Create backend API endpoints (optional)
4. ⏭️ Add product images
5. ⏭️ Customize styling/content

---

**Ready?** Start with Step 1: Rebuild the DevContainer!
