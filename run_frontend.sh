#!/bin/bash

# Change directory to frontend
cd frontend || { echo "Directory 'frontend' not found"; exit 1; }

# Run npm build
npm run build || { echo "npm build failed"; exit 1; }

# Change directory to dist
cd dist || { echo "Directory 'dist' not found"; exit 1; }

# Start Python HTTP server on port 3000
python3 -m http.server 3000