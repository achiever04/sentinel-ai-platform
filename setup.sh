#!/bin/bash

echo "======================================"
echo "Sentinel AI Platform - Setup Script"
echo "======================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Ubuntu
if [[ ! -f /etc/os-release ]] || ! grep -q "Ubuntu" /etc/os-release; then
    echo -e "${RED}Warning: Optimized for Ubuntu.${NC}"
fi

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Python 3.10+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}Python OK: $PYTHON_VERSION${NC}"

# Update system
echo -e "${YELLOW}Updating system packages...${NC}"
sudo apt-get update

# Install system dependencies
echo -e "${YELLOW}Installing system dependencies...${NC}"
sudo apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    python3-dev \
    python3-pip \
    python3-venv \
    libopencv-dev \
    libboost-all-dev \
    libgtk-3-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libtbb2 \
    libtbb-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libdc1394-22-dev \
    libatlas-base-dev \
    gfortran \
    ffmpeg \
    redis-server \
    portaudio19-dev \
    espeak \
    libmagic1

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies (10-15 minutes)...${NC}"
pip install -r requirements.txt

# Create directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p data/{database,models,uploads,videos,synthetic_faces}
mkdir -p data/models/{face_recognition,behavior,federated}
mkdir -p logs

# Copy .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
fi

# Start Redis
echo -e "${YELLOW}Starting Redis...${NC}"
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
python3 scripts/setup_database.py

# Generate synthetic data
echo -e "${YELLOW}Generating synthetic data...${NC}"
python3 scripts/generate_synthetic_data.py

# Create admin user
echo -e "${YELLOW}Creating default users...${NC}"
python3 scripts/create_admin.py

# Install frontend dependencies
if [ -d "frontend" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
fi

echo -e "${GREEN}======================================"
echo -e "Setup Complete!"
echo -e "======================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Review .env file"
echo "2. Start backend: ./run_backend.sh"
echo "3. Start frontend: ./run_frontend.sh"
echo "4. Access: http://localhost:3000"
echo ""
echo -e "${YELLOW}Default Credentials:${NC}"
echo "Admin: admin / admin123"
echo "Operator: operator / operator123"