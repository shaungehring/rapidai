#!/bin/bash
# Publishing script for RapidAI
# Usage: ./scripts/publish.sh [test|prod]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

error() {
    echo -e "${RED}✗ ${1}${NC}"
    exit 1
}

# Parse arguments
MODE=${1:-test}

if [[ "$MODE" != "test" && "$MODE" != "prod" ]]; then
    error "Invalid mode. Use 'test' or 'prod'"
fi

echo ""
info "RapidAI Publishing Script"
echo "=========================="
echo ""

# Check we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    error "pyproject.toml not found. Run this from the project root."
fi

# Get version
VERSION=$(grep "^version" pyproject.toml | head -1 | cut -d'"' -f2)
info "Version: ${VERSION}"

# Step 1: Pre-flight checks
info "Running pre-flight checks..."

# Check if git repo is clean
if ! git diff-index --quiet HEAD --; then
    warning "Uncommitted changes detected"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Aborted by user"
    fi
fi

# Check if build tools are installed
if ! command -v python &> /dev/null; then
    error "Python not found"
fi

if ! python -c "import build" 2>/dev/null; then
    warning "build module not found. Installing..."
    pip install build
fi

if ! python -c "import twine" 2>/dev/null; then
    warning "twine module not found. Installing..."
    pip install twine
fi

success "Pre-flight checks passed"

# Step 2: Run tests
info "Running tests..."
if ! pytest tests/ -v --tb=short; then
    error "Tests failed. Fix them before publishing."
fi
success "All tests passed"

# Step 3: Verify imports
info "Verifying package imports..."
if ! python -c "from rapidai import App, LLM, background, monitor" 2>/dev/null; then
    error "Package imports failed"
fi
success "Imports verified"

# Step 4: Clean previous builds
info "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/
success "Build artifacts cleaned"

# Step 5: Build package
info "Building package..."
if ! python -m build; then
    error "Build failed"
fi

# Verify build artifacts
if [ ! -f "dist/rapidai-${VERSION}.tar.gz" ] || [ ! -f "dist/rapidai-${VERSION}-py3-none-any.whl" ]; then
    error "Build artifacts not found"
fi

success "Package built successfully"
ls -lh dist/

# Step 6: Validate distribution
info "Validating distribution..."
if ! twine check dist/*; then
    error "Distribution validation failed"
fi
success "Distribution validated"

# Step 7: Upload
if [ "$MODE" = "test" ]; then
    info "Uploading to TestPyPI..."
    echo ""
    warning "This will upload to TEST PyPI"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Aborted by user"
    fi

    if ! twine upload --repository testpypi dist/*; then
        error "Upload to TestPyPI failed"
    fi

    success "Uploaded to TestPyPI"
    echo ""
    info "Test installation:"
    echo "  python -m venv test_env"
    echo "  source test_env/bin/activate"
    echo "  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ rapidai"
    echo "  python -c 'import rapidai; print(rapidai.__version__)'"
    echo ""
    info "View at: https://test.pypi.org/project/rapidai/${VERSION}/"

else
    info "Uploading to PyPI..."
    echo ""
    warning "⚠️  This will publish to PRODUCTION PyPI ⚠️"
    warning "Version ${VERSION} cannot be re-uploaded once published"
    echo ""
    read -p "Are you absolutely sure? (yes/no) " -r
    echo
    if [[ ! $REPLY = "yes" ]]; then
        error "Aborted by user. Type 'yes' to confirm."
    fi

    # Create git tag
    if ! git tag -l | grep -q "v${VERSION}"; then
        info "Creating git tag v${VERSION}..."
        git tag -a "v${VERSION}" -m "Release version ${VERSION}"
        git push origin "v${VERSION}"
        success "Git tag created"
    fi

    if ! twine upload dist/*; then
        error "Upload to PyPI failed"
    fi

    success "🎉 Published to PyPI!"
    echo ""
    info "Package is now live at: https://pypi.org/project/rapidai/${VERSION}/"
    echo ""
    info "Install with:"
    echo "  pip install rapidai"
    echo ""
    info "Next steps:"
    echo "  1. Create GitHub release: https://github.com/shaungehring/rapidai/releases/new"
    echo "  2. Announce on social media"
    echo "  3. Update documentation"
    echo ""
fi

echo ""
success "Done!"
