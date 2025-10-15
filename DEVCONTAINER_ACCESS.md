# DevContainer Web App Access - Troubleshooting

## ✅ Solution Applied

The Vite configuration has been updated to work in devcontainers:

### What Changed in `vite.config.js`:
```javascript
server: {
  host: '0.0.0.0',      // ✅ Listen on all interfaces (required for devcontainer)
  port: 3000,
  strictPort: true,
  watch: {
    usePolling: true    // ✅ File watching in containers
  }
}
```

## 🚀 How to Access the Frontend

### Method 1: VS Code Port Forwarding (Recommended)

1. Start the dev server:
   ```bash
   cd /workspace/frontend
   npm run dev
   ```

2. Look for the VS Code notification:
   - "Your application running on port 3000 is available"
   - Click "Open in Browser"

3. Or manually:
   - Click the "Ports" tab at the bottom of VS Code
   - Find port 3000
   - Click the globe icon or right-click → "Open in Browser"

### Method 2: Direct URL

Access via the forwarded port URL provided by VS Code:
- Usually: `http://localhost:3000`
- Or: `https://<your-codespace-name>-3000.preview.app.github.dev` (if using GitHub Codespaces)

## 🔍 Verifying It's Running

After running `npm run dev`, you should see:

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://172.x.x.x:3000/
  ➜  press h + enter to show help
```

The "Network" URL shows it's listening on `0.0.0.0` (all interfaces).

## 🐛 Troubleshooting

### Issue: "Cannot GET /" or connection refused

**Solution:**
1. Make sure the dev server is running (see output above)
2. Check VS Code port forwarding:
   - Open "Ports" tab at bottom of VS Code
   - Port 3000 should be listed
   - Status should be "forwarded" or green
3. Try stopping and restarting:
   ```bash
   # Press Ctrl+C to stop
   npm run dev
   ```

### Issue: Port already in use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or change port in vite.config.js
```

### Issue: Changes not reflecting

The configuration includes `usePolling: true` for file watching, but if it still doesn't work:

```bash
# Restart the dev server
# Press Ctrl+C, then:
npm run dev
```

### Issue: White screen / no content

1. Check browser console (F12) for errors
2. Check the terminal for Vite errors
3. Verify dependencies are installed:
   ```bash
   cd /workspace/frontend
   npm install
   ```

## 📋 Quick Checklist

- [ ] Node.js and npm are installed (check: `node --version`)
- [ ] Dependencies are installed (`npm install`)
- [ ] Dev server is running (`npm run dev`)
- [ ] Port 3000 shows as forwarded in VS Code Ports tab
- [ ] Browser is pointing to the forwarded URL

## 🎯 Expected Behavior

When working correctly:
1. Run `npm run dev`
2. See Vite startup message with URLs
3. VS Code shows port forwarding notification
4. Click notification or use Ports tab
5. Browser opens to Zava store homepage

## 💡 DevContainer-Specific Tips

1. **Host Configuration**: `host: '0.0.0.0'` is essential for devcontainers
2. **Port Forwarding**: VS Code automatically forwards ports listed in devcontainer.json
3. **File Watching**: `usePolling: true` helps with file watching in mounted volumes
4. **Rebuild**: If issues persist after changes, rebuild the container

## 🔧 Alternative: Preview with Simple HTTP Server

If Vite issues persist, you can build and serve:

```bash
cd /workspace/frontend
npm run build
cd dist
python3 -m http.server 3000
```

Then access via the forwarded port.

---

**Still having issues?** Check:
1. VS Code "Ports" panel for port forwarding status
2. Browser console (F12) for JavaScript errors
3. Terminal output for Vite/build errors
