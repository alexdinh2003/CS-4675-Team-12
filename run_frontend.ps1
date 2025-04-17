# Navigate to the frontend directory
Set-Location -Path "frontend" -ErrorAction Stop

# Run the build process
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed"
    exit 1
}

# Navigate to the dist directory
Set-Location -Path "dist" -ErrorAction Stop

# Serve the frontend files
python -m http.server 3000