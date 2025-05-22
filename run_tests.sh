#!/bin/bash

# Run integration tests for the Poly Micro Manager Backend
echo "Running integration tests for Poly Micro Manager Backend API"
echo "============================================================"

# Install dependencies if needed
echo "Checking dependencies..."
uv pip install -r requirements.txt

# Run pytest with verbose output
echo "Running tests..."
uv run pytest tests/ -v

# Show summary
if [ $? -eq 0 ]; then
    echo "============================================================"
    echo "✅ All tests passed successfully!"
else
    echo "============================================================"
    echo "❌ Some tests failed. Please check the output above for details."
fi
