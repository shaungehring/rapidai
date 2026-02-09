#!/bin/bash
# RapidAI Setup Script

set -e

echo "🚀 Setting up RapidAI development environment..."
echo ""

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"

# Install package in editable mode with dev dependencies
echo "Installing RapidAI with dependencies..."
pip install -e ".[dev,anthropic,openai]" > /dev/null 2>&1
echo "✓ RapidAI installed"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - OPENAI_API_KEY"
else
    echo "✓ .env file already exists"
fi

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install > /dev/null 2>&1
echo "✓ Pre-commit hooks installed"

# Run tests
echo ""
echo "Running tests..."
pytest -v

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Edit .env and add your API keys"
echo "  3. Run an example: python examples/chatbot.py"
echo "  4. Read QUICKSTART.md for more information"
echo ""
echo "Happy coding! 🎉"
