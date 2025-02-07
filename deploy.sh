#!/bin/bash

# Universal Deployment Script for DOU Blockchain

# Check for required dependencies
check_dependencies() {
    echo "Checking system dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 is required. Please install it."
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        echo "pip3 is required. Please install it."
        exit 1
    fi
    
    # Optional: Check Docker
    if ! command -v docker &> /dev/null; then
        echo "Docker not found. Falling back to local Python deployment."
    fi
}

# Create virtual environment
setup_venv() {
    echo "Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
}

# Docker deployment
docker_deploy() {
    if command -v docker &> /dev/null; then
        echo "Building Docker image..."
        docker build -t dou-blockchain .
        
        echo "Creating persistent data directory..."
        mkdir -p ./data
        
        echo "Running DOU Blockchain in Docker..."
        docker run -v $(pwd)/data:/app/data \
                   -e DOU_DATA_DIR=/app/data \
                   dou-blockchain create
    else
        echo "Docker not available. Skipping containerized deployment."
    fi
}

# Local Python deployment
local_deploy() {
    echo "Deploying locally..."
    python3 cli.py create
}

# Main deployment function
main() {
    check_dependencies
    setup_venv
    
    # Offer deployment options
    echo "Deployment Options:"
    echo "1. Docker Deployment"
    echo "2. Local Python Deployment"
    read -p "Choose deployment method (1/2): " choice
    
    case $choice in
        1) docker_deploy ;;
        2) local_deploy ;;
        *) echo "Invalid choice. Defaulting to local deployment."; local_deploy ;;
    esac
}

# Run the deployment
main
