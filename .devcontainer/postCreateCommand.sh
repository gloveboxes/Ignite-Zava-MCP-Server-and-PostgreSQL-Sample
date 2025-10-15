#!/usr/bin/env bash

echo "Installing frontend dependencies"
cd /workspace/frontend && npm install

echo "Setup complete!"
echo "- Python environment: ready"
echo "- Node.js: $(node --version)"
echo "- npm: $(npm --version)"
echo "- Frontend dependencies: installed"
