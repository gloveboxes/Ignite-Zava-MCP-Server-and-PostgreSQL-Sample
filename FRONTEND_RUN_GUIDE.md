# 🚀 Running the Frontend in DevContainer - Step by Step

## ✅ The Fix is Applied!

Your `vite.config.js` has been updated with devcontainer-compatible settings:
- ✅ Listens on `0.0.0.0` (all network interfaces)
- ✅ File watching enabled for containers
- ✅ Port 3000 configured

## 📋 Follow These Steps

### Step 1: Start the Dev Server
```bash
cd /workspace/frontend
npm run dev
```

### Step 2: Look for This Output
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://172.x.x.x:3000/
  ➜  press h + enter to show help
```

✅ If you see this, Vite is running correctly!

### Step 3: Access via VS Code Port Forwarding

You'll see one of these:

#### Option A: Notification Popup
```
┌─────────────────────────────────────────────┐
│ Your application running on port 3000 is   │
│ available. [Open in Browser]               │
└─────────────────────────────────────────────┘
```
👉 **Click "Open in Browser"**

#### Option B: Ports Tab
1. Look at the bottom of VS Code
2. Click the **"PORTS"** tab (next to Terminal, Problems, etc.)
3. You should see:
   ```
   PORT    LABEL            ADDRESS
   3000    Frontend (Vue)   localhost:3000
   ```
4. Right-click on port 3000 → **"Open in Browser"**
5. Or click the globe 🌐 icon next to it

### Step 4: Browser Opens
The Zava store homepage should load with:
- Hero section "Welcome to ZAVA"
- Category cards
- Featured products
- Navigation menu

## 🎉 Success!

If you see the Zava store, everything is working! Try:
- ✅ Clicking on categories in the navigation
- ✅ Browsing products
- ✅ Clicking on a product to see details
- ✅ Viewing store locations

## ❌ Troubleshooting

### Problem: Can't see the Ports tab
**Solution:** 
- Press `Ctrl+` ` (backtick) to open terminal panel
- Look for tabs: PROBLEMS | OUTPUT | DEBUG CONSOLE | TERMINAL | **PORTS**
- Click PORTS

### Problem: Port 3000 not showing in Ports tab
**Solution:**
1. Make sure `npm run dev` is running (check terminal)
2. Wait 5-10 seconds after starting
3. If still not showing, manually forward:
   - In Ports tab, click "Forward a Port"
   - Enter: 3000
   - Press Enter

### Problem: Browser shows "This site can't be reached"
**Solution:**
1. Check Vite is running (see Step 2 output)
2. Use the Ports tab (don't type URL manually)
3. Try clicking the port again
4. If using Edge/Chrome, try Firefox or vice versa

### Problem: Port says "Forwarded" but browser shows error
**Solution:**
```bash
# Stop the server (Ctrl+C)
# Restart it
npm run dev
# Click the port again in VS Code
```

### Problem: White screen / blank page
**Solution:**
1. Open browser console (F12)
2. Look for errors
3. Common fixes:
   ```bash
   # Reinstall dependencies
   cd /workspace/frontend
   rm -rf node_modules
   npm install
   npm run dev
   ```

## 🔍 How to Know It's Working

### In Terminal:
```
✅ VITE v5.x.x  ready in xxx ms
✅ Network: http://172.x.x.x:3000/
```

### In VS Code Ports Tab:
```
✅ Port 3000 showing
✅ Status: "Forwarded" or green
```

### In Browser:
```
✅ Zava store loads
✅ Can see navigation menu
✅ Can see featured products
✅ No errors in console (F12)
```

## 📱 Mobile Testing

To test on your phone (same network):
1. In Ports tab, right-click port 3000
2. Select "Port Visibility" → "Public"
3. Use the provided public URL

## 💻 Multiple Terminals

You can run multiple things simultaneously:

**Terminal 1:** Frontend
```bash
cd /workspace/frontend
npm run dev
```

**Terminal 2:** Backend (when you create it)
```bash
cd /workspace
python -m app.api.server
```

**Terminal 3:** Other commands
```bash
# Available for git, testing, etc.
```

## 🎯 What to Expect

### Performance
- First load: 1-3 seconds
- Hot reload: < 1 second
- Navigation: Instant

### Features Working
- ✅ Homepage with featured products
- ✅ Category navigation (dropdowns)
- ✅ Product listings
- ✅ Product detail pages
- ✅ Store locations
- ✅ Responsive design
- ⏸️ Cart (placeholder/mock)
- ⏸️ Login (placeholder/mock)
- ⏸️ Checkout (placeholder/mock)

## 🛠️ Development Tips

### Hot Reload
Changes to Vue files auto-refresh the browser. Just save your file!

### VS Code Extensions (Recommended)
- Vue Language Features (Volar)
- Vue DevTools (browser extension)
- ESLint (if you add it)

### Debugging
- Browser DevTools: F12 → Console/Network tabs
- Vue DevTools: Browser extension for component inspection

---

**Ready?** Run `npm run dev` and click the port forwarding link! 🚀
