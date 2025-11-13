#!/bin/bash

# Setup script for Claudes Deep Coding

set -e

echo "=== Claudes Deep Coding Setup ==="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "⚠ Docker is not installed. Please install Docker to run Neo4j."
    echo "  Visit: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✓ Docker is installed"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "⚠ docker-compose is not installed. Please install docker-compose."
    exit 1
fi
echo "✓ docker-compose is available"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -e .
echo "✓ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠ Please edit .env and add your ANTHROPIC_API_KEY"
fi

# Start Neo4j
echo ""
read -p "Do you want to start Neo4j now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting Neo4j..."
    docker-compose up -d
    echo "✓ Neo4j started"
    echo ""
    echo "Neo4j is available at:"
    echo "  - Browser: http://localhost:7474"
    echo "  - Bolt: bolt://localhost:7687"
    echo "  - Username: neo4j"
    echo "  - Password: deepcoding123"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY"
echo "2. Run an example: python examples/basic_usage.py"
echo "3. Access Neo4j browser: http://localhost:7474"
echo ""
