import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// Plugin to serve images from workspace root
function serveWorkspaceImages() {
  return {
    name: 'serve-workspace-images',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (req.url?.startsWith('/images/')) {
          const imagePath = path.resolve(__dirname, '..', req.url)
          if (fs.existsSync(imagePath)) {
            // Set proper content type based on file extension
            const ext = path.extname(imagePath).toLowerCase()
            const contentTypes = {
              '.jpg': 'image/jpeg',
              '.jpeg': 'image/jpeg',
              '.png': 'image/png',
              '.gif': 'image/gif',
              '.webp': 'image/webp',
              '.svg': 'image/svg+xml'
            }
            res.setHeader('Content-Type', contentTypes[ext] || 'application/octet-stream')
            res.setHeader('Cache-Control', 'public, max-age=31536000')
            fs.createReadStream(imagePath).pipe(res)
            return
          }
        }
        next()
      })
    }
  }
}

export default defineConfig({
  plugins: [vue(), serveWorkspaceImages()],
  server: {
    host: '0.0.0.0',  // Listen on all network interfaces (required for devcontainer)
    port: 3000,
    strictPort: true,
    watch: {
      usePolling: true  // Required for file watching in some container environments
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8091',
        changeOrigin: true,
      }
    }
  }
})
