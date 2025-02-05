#!/bin/bash

echo "=== Python Environment Check ==="
python3 --version
echo

echo "=== Project Structure Check ==="
tree . -I '__pycache__|*.pyc|.git|logs|*.log'
echo

echo "=== Required Files Check ==="
required_files=("bot.py" "config.py" ".env" "utils/logger.py")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
    fi
done
echo

echo "=== Python Dependencies Check ==="
echo "Checking required packages..."
packages=(
    "anthropic"
    "requests"
    "python-dotenv"
)

for package in "${packages[@]}"; do
    if pip show $package > /dev/null 2>&1; then
        version=$(pip show $package | grep Version | cut -d' ' -f2)
        echo "✓ $package (version $version)"
    else
        echo "✗ $package not installed"
    fi
done
echo

echo "=== Environment Variables Check ==="
if [ -f ".env" ]; then
    echo "Checking .env file for required variables (presence only, not values)..."
    required_vars=(
        "CLAUDE_API_KEY"
        "CLAUDE_MODEL"
    )
    
    for var in "${required_vars[@]}"; do
        if grep -q "^$var=" .env; then
            echo "✓ $var is set"
        else
            echo "✗ $var is missing"
        fi
    done
else
    echo "✗ .env file not found"
fi
echo

echo "=== Database Check ==="
if [ -f "market_data.db" ]; then
    echo "✓ market_data.db exists"
    echo "Database size: $(du -h market_data.db | cut -f1)"
else
    echo "✗ market_data.db not found (will be created on first run)"
fi
echo

echo "=== Log Directory Check ==="
if [ -d "logs" ]; then
    echo "✓ logs directory exists"
else
    echo "✗ logs directory missing (will be created on first run)"
fi
