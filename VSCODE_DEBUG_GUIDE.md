# 🚀 VS Code Debug Configuration for Web App

## ✅ What Was Added

Added debug configurations to `.vscode/launch.json` for running the full stack web application.

---

## 🎯 Available Configurations

### Individual Configurations

#### 1. 🔧 Backend API Server (Port 8091)
Starts the FastAPI backend server with debugging enabled.
- **Port**: 8091
- **Type**: Python debugpy
- **Module**: `app.api.app`

#### 2. 🎨 Frontend Dev Server (Port 3000)
Starts the Vue.js frontend with Vite dev server.
- **Port**: 3000
- **Type**: Node terminal
- **Command**: `npm run dev`

### Compound Configuration

#### 🌐 Full Stack Web App (Frontend + Backend)
**This is the main one you want!** Starts both frontend and backend together.
- Launches both servers simultaneously
- Separate terminals for each
- Stop all with one click

---

## 🚀 How to Use

### Method 1: Debug Panel (Recommended)

1. **Open Debug Panel**: Click the debug icon in the left sidebar (or press `Ctrl+Shift+D` / `Cmd+Shift+D`)

2. **Select Configuration**: In the dropdown at the top, choose:
   ```
   🌐 Full Stack Web App (Frontend + Backend)
   ```

3. **Start Debugging**: Click the green play button (or press `F5`)

4. **Result**: 
   - Backend API starts in one terminal (Port 8091)
   - Frontend starts in another terminal (Port 3000)
   - Both are debuggable!

### Method 2: Command Palette

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: "Debug: Select and Start Debugging"
3. Choose: "🌐 Full Stack Web App (Frontend + Backend)"

### Method 3: Quick Access

Press `F5` and select the configuration from the dropdown.

---

## 🔍 What Happens When You Start

### Backend API (Terminal: "Backend API")
```
INFO:     🚀 Starting Zava API Server...
INFO:     ✅ Database connection pool created
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8091
```

### Frontend (Terminal: "Frontend")
```
VITE v5.x.x  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: http://0.0.0.0:3000/
```

---

## 🛑 How to Stop

### Stop All Servers
Click the **red square** (Stop) button in the debug toolbar.
This will stop both frontend and backend together.

### Stop Individual Server
Go to the specific terminal and press `Ctrl+C`.

---

## 🐛 Debugging Features

### Backend Python Debugging
- ✅ Set breakpoints in Python files
- ✅ Inspect variables
- ✅ Step through code
- ✅ View call stack
- ✅ Debug console

### Frontend Debugging
- Limited debugging in terminal
- For full frontend debugging, use browser DevTools
- Or attach Chrome debugger (separate configuration needed)

---

## 📊 Debug Toolbar

When debugging starts, you'll see a toolbar with:
- ▶️ Continue (F5)
- ⏭️ Step Over (F10)
- ⏬ Step Into (F11)
- ⏫ Step Out (Shift+F11)
- 🔄 Restart (Ctrl+Shift+F5)
- ⏹️ Stop (Shift+F5)

---

## 🔧 Configuration Details

### Backend Configuration
```json
{
    "name": "🔧 Backend API Server (Port 8091)",
    "type": "debugpy",
    "request": "launch",
    "module": "app.api.app",
    "console": "integratedTerminal",
    "consoleName": "Backend API",
    "cwd": "${workspaceFolder}",
    "env": {
        "PYTHONPATH": "${workspaceFolder}"
    }
}
```

### Frontend Configuration
```json
{
    "name": "🎨 Frontend Dev Server (Port 3000)",
    "type": "node-terminal",
    "request": "launch",
    "command": "npm run dev",
    "cwd": "${workspaceFolder}/frontend"
}
```

### Compound Configuration
```json
{
    "name": "🌐 Full Stack Web App (Frontend + Backend)",
    "configurations": [
        "🔧 Backend API Server (Port 8091)",
        "🎨 Frontend Dev Server (Port 3000)"
    ],
    "stopAll": true
}
```

---

## 🎯 Other Available Configurations

Your `launch.json` also includes:

### MCP Servers
- 📊 Sales Analysis MCP Server (Port 8000)
- 🏪 Supplier MCP Server (Port 8001)
- 💰 Finance MCP Server (Port 8002)
- 🔥 All MCP Servers (Compound Launch)

### Other
- 🤵 Agent UI

You can run any of these individually or in combination!

---

## 💡 Pro Tips

### Tip 1: Auto-Restart
Both servers have auto-reload enabled:
- **Backend**: Python files changes trigger restart
- **Frontend**: Vue/JS file changes trigger hot module reload

### Tip 2: Terminal Management
Each server gets its own terminal:
- Switch between terminals using the dropdown
- Keep them open to see logs
- Color-coded for easy identification

### Tip 3: Debugging Backend
Set breakpoints in your API code:
1. Open `/workspace/app/api/app.py`
2. Click in the gutter to set a breakpoint (red dot)
3. Make a request to the API
4. Debugger will pause at your breakpoint!

### Tip 4: Quick Test
After starting, test both servers:
```bash
# Backend
curl http://localhost:8091/health

# Frontend  
curl http://localhost:3000
```

Or just open browser to `http://localhost:3000`

---

## 🚀 Quick Start Workflow

1. **Start the app**:
   - Press `F5`
   - Select "🌐 Full Stack Web App"

2. **Wait for servers to start** (~3-5 seconds)

3. **Open browser**: `http://localhost:3000`

4. **Make changes**:
   - Edit Python files → Backend auto-restarts
   - Edit Vue files → Frontend hot-reloads

5. **Stop when done**:
   - Click stop button or `Shift+F5`

---

## 🎉 You're All Set!

Now you can start the entire web application with a single click in VS Code!

Press **F5** and select **"🌐 Full Stack Web App (Frontend + Backend)"** to get started! 🚀
