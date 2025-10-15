# DevContainer Rebuild Instructions

## What's Been Updated

The devcontainer has been updated to include:
- ✅ **Node.js 20.x** - Latest LTS version
- ✅ **npm** - Latest version
- ✅ **Automatic frontend dependency installation** - Runs on container creation
- ✅ **Port forwarding** for:
  - Port 8005: Web Chat App
  - Port 3000: Frontend (Vue.js)
  - Port 8091: Backend API

## How to Rebuild the DevContainer

### Option 1: VS Code Command Palette (Recommended)

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: **"Dev Containers: Rebuild Container"**
3. Select it and wait for the rebuild to complete (5-10 minutes)

### Option 2: VS Code Command Palette (Clean Rebuild)

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: **"Dev Containers: Rebuild Container Without Cache"**
3. Select it (this will take longer but ensures a clean build)

### Option 3: Manual Rebuild

```bash
# Close VS Code
# From your local terminal (not in the container):
cd /path/to/your/project
docker-compose down
docker-compose build --no-cache
# Reopen in VS Code
```

## After Rebuild

Once the container rebuilds, the `postCreateCommand.sh` script will automatically:
1. Restore .NET dependencies
2. Install Node.js and npm (via Dockerfile)
3. Install frontend npm dependencies

You can verify the installation by running:

```bash
# Check Node.js version
node --version
# Should output: v20.x.x

# Check npm version
npm --version
# Should output: 10.x.x

# Check frontend dependencies
cd /workspace/frontend
npm list
```

## Running the Frontend

After the rebuild:

```bash
cd /workspace/frontend
npm run dev
```

The frontend will be available at: `http://localhost:3000`

## Ports

The following ports are automatically forwarded:
- **3000** - Vue.js Frontend (dev server)
- **8005** - Web Chat App
- **8091** - Backend API (when you create it)

## Troubleshooting

### If Node.js is not found after rebuild:

```bash
# Check if Node.js is installed
which node

# If not found, manually run:
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
```

### If frontend dependencies fail to install:

```bash
cd /workspace/frontend
rm -rf node_modules package-lock.json
npm install
```

### If rebuild fails:

1. Try "Rebuild Without Cache"
2. Check Docker has enough memory (8GB+ recommended)
3. Check Docker disk space
4. Restart Docker Desktop

## Changes Made to DevContainer

### `.devcontainer/Dockerfile`
- Added Node.js 20.x installation
- Added npm installation and upgrade

### `.devcontainer/devcontainer.json`
- Added port 3000 forwarding (Frontend)
- Added port 8091 forwarding (Backend API)
- Added `postCreateCommand` to install frontend dependencies

### `.devcontainer/postCreateCommand.sh`
- Added frontend npm install command
- Added status messages

## Next Steps

1. **Rebuild the container** using one of the methods above
2. **Start the frontend**: `cd /workspace/frontend && npm run dev`
3. **Access the frontend**: Open `http://localhost:3000` in your browser
4. **Create the backend API** (optional - frontend works with mock data)

---

**Note**: The rebuild will take 5-15 minutes depending on your internet connection and Docker performance.
