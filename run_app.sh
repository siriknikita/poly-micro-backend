#!/bin/bash

# Copy example environment if .env doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example"
    cp .env.example .env
fi

# Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Run the app
echo "Starting Poly Micro Manager API..."
python run.py
