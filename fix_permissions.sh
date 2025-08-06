#!/bin/bash

# Fix Permissions Script
# This script fixes file and directory permissions for Pinmaker

echo "🔧 Fixing Pinmaker Permissions..."

# Navigate to application directory
cd /opt/Pinmaker

# Fix ownership
echo "👤 Fixing ownership..."
sudo chown -R pinmaker:pinmaker /opt/Pinmaker

# Fix directory permissions
echo "📁 Fixing directory permissions..."
find /opt/Pinmaker -type d -exec chmod 755 {} \;

# Fix file permissions
echo "📄 Fixing file permissions..."
find /opt/Pinmaker -type f -exec chmod 644 {} \;

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x /opt/Pinmaker/*.sh
chmod +x /opt/Pinmaker/venv/bin/*

# Fix log directory permissions
echo "📝 Fixing log permissions..."
mkdir -p /opt/Pinmaker/logs
chmod 755 /opt/Pinmaker/logs

# Fix upload directory permissions
echo "📤 Fixing upload permissions..."
mkdir -p /opt/Pinmaker/uploads
chmod 755 /opt/Pinmaker/uploads

# Fix temp directory permissions
echo "🗂️ Fixing temp permissions..."
mkdir -p /opt/Pinmaker/temp
chmod 755 /opt/Pinmaker/temp

# Fix static directory permissions
echo "🌐 Fixing static permissions..."
mkdir -p /opt/Pinmaker/static
chmod 755 /opt/Pinmaker/static

echo "✅ Permissions fixed successfully!"

# Show final permissions
echo ""
echo "📊 Current permissions:"
ls -la /opt/Pinmaker/ | head -10