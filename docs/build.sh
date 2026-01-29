#!/bin/bash
# Build and serve MkDocs documentation

set -e

echo "🚀 Building Cold Chain System API Documentation..."

# Change to docs directory
cd "$(dirname "$0")"

# Check if MkDocs is installed
if ! command -v mkdocs &> /dev/null; then
    echo "📦 Installing MkDocs dependencies..."
    pip install -r requirements.txt
fi

# Build documentation
echo "🔨 Building documentation..."
mkdocs build --clean

echo "✅ Documentation built successfully!"
echo "📄 Output directory: site/"
echo ""
echo "To serve documentation locally, run:"
echo "  mkdocs serve"
echo ""
echo "To deploy to GitHub Pages, run:"
echo "  mkdocs gh-deploy"
