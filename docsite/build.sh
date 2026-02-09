#!/bin/bash
# Build script for RapidAI documentation

echo "🚀 Building RapidAI Documentation..."
echo ""

# Check if mkdocs is installed
if ! command -v mkdocs &> /dev/null; then
    echo "❌ MkDocs not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Clean previous build
echo "🧹 Cleaning previous build..."
rm -rf site/

# Build the site
echo "🔨 Building static site..."
mkdocs build

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build complete!"
    echo "📁 Output directory: site/"
    echo ""
    echo "To serve locally:"
    echo "  mkdocs serve"
    echo ""
    echo "To deploy to GitHub Pages:"
    echo "  mkdocs gh-deploy"
else
    echo "❌ Build failed!"
    exit 1
fi
