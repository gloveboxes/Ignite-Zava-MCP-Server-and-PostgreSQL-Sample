# 🎯 Quick Start: Launch Full Stack Web App in VS Code

## ✅ What Was Added

Added a **compound debug configuration** to VS Code that launches both frontend and backend servers together with one click!

---

## 🚀 How to Launch (3 Easy Steps)

### Step 1: Open Debug Panel
Click the **Debug icon** in the left sidebar (looks like a play button with a bug)

Or press: `Ctrl+Shift+D` (Windows/Linux) or `Cmd+Shift+D` (Mac)

### Step 2: Select Configuration
In the dropdown at the top of the debug panel, select:

```
🌐 Full Stack Web App (Frontend + Backend)
```

### Step 3: Start!
Click the **green play button** or press `F5`

---

## ✨ What Happens

Two terminals will open automatically:

### Terminal 1: "Backend API"
```bash
INFO:     🚀 Starting Zava API Server...
INFO:     ✅ Database connection pool created
INFO:     Uvicorn running on http://0.0.0.0:8091
```
✅ **Backend API**: http://localhost:8091

### Terminal 2: "Frontend"  
```bash
VITE v5.x.x  ready in 500 ms
➜  Local:   http://localhost:3000/
```
✅ **Frontend App**: http://localhost:3000

---

## 🌐 Open Your Browser

Once both servers are running (3-5 seconds), open:

**http://localhost:3000**

You should see the Zava popup store homepage with real products from the database!

---

## 🛑 How to Stop

Click the **red square (Stop)** button in the debug toolbar.

This will stop both servers at once.

Or press: `Shift+F5`

---

## 🐛 Debugging Features

### Set Breakpoints in Backend
1. Open `/workspace/app/api/app.py`
2. Click in the gutter (left of line numbers) to set a breakpoint
3. Make a request to the API
4. VS Code will pause at your breakpoint!

### View Variables
- Hover over variables to see their values
- Use the **Variables** panel in the debug sidebar
- Use the **Debug Console** to execute code

### Step Through Code
- **Continue** (F5): Run until next breakpoint
- **Step Over** (F10): Execute current line
- **Step Into** (F11): Go into function
- **Step Out** (Shift+F11): Exit current function

---

## 🔄 Auto-Reload

Both servers have auto-reload enabled:

### Backend (Python)
Edit any `.py` file → Server automatically restarts

### Frontend (Vue/JS)
Edit any `.vue`, `.js`, or `.css` file → Browser automatically updates (hot module reload)

---

## 📦 Available Configurations

When you open the debug dropdown, you'll see:

### Web App Configurations
- **🌐 Full Stack Web App (Frontend + Backend)** ← Use this!
- 🔧 Backend API Server (Port 8091) - Backend only
- 🎨 Frontend Dev Server (Port 3000) - Frontend only

### MCP Server Configurations
- 📊 Sales Analysis MCP Server (Port 8000)
- 🏪 Supplier MCP Server (Port 8001)
- 💰 Finance MCP Server (Port 8002)
- 🔥 All MCP Servers (Compound Launch)

### Other
- 🚀 All MCP Servers (Sales + Supplier + Finance)
- 🤵 Agent UI

---

## 🧪 Quick Test

After launching, test in a terminal:

```bash
# Test backend health
curl http://localhost:8091/health

# Test featured products API
curl http://localhost:8091/api/products/featured?limit=3

# Or just open your browser to:
# http://localhost:3000
```

---

## 💡 Pro Tips

### Tip 1: Keep Terminals Open
Don't close the terminal windows - you'll see useful logs:
- API requests
- Errors and warnings
- Database queries
- Frontend build info

### Tip 2: Use the Debug Console
While debugging, open the **Debug Console** (bottom panel):
- Execute Python code in the backend context
- Check variable values
- Test functions

### Tip 3: Multiple Stops/Starts
You can stop and restart as many times as needed:
- Ports are properly cleaned up
- No manual cleanup required

### Tip 4: View All Terminals
Click the **Terminal** dropdown to switch between:
- Backend API terminal
- Frontend terminal
- Other terminals

---

## 🐛 Troubleshooting

### "Port already in use"
Stop any existing processes:
```bash
# Stop backend
pkill -f "app.api.app"

# Stop frontend
pkill -f "vite"

# Or kill specific port
lsof -ti:8091 | xargs kill
lsof -ti:3000 | xargs kill
```

### Backend won't start
Check environment variables:
```bash
env | grep POSTGRES
```

### Frontend won't start
Make sure dependencies are installed:
```bash
cd /workspace/frontend
npm install
```

---

## 🎉 Summary

You now have a **one-click debug configuration** that:

✅ Starts both frontend and backend servers
✅ Opens separate terminals for each
✅ Enables Python debugging with breakpoints
✅ Supports auto-reload for both servers
✅ Stops everything with one click

**Press F5 and select "🌐 Full Stack Web App" to get started!** 🚀

---

## 📖 See Also

- **BACKEND_API_COMPLETE.md** - Backend API documentation
- **FRONTEND_RUN_GUIDE.md** - Frontend setup guide
- **API_BACKEND_GUIDE.md** - API endpoint reference
