#!/bin/bash

# SmartReports Startup Script
# This script starts both the backend (FastAPI) and frontend (React + Vite)

set -e

echo "========================================="
echo "  SmartReports - Startup Script"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    exit 1
fi

echo -e "${BLUE}Checking prerequisites...${NC}"

# Check if Redis is running
if ! redis-cli ping &> /dev/null; then
    echo -e "${YELLOW}Warning: Redis is not running. Please start Redis first.${NC}"
    echo "On macOS: brew services start redis"
    echo "On Linux: sudo systemctl start redis"
    exit 1
fi

echo -e "${GREEN}✓ Redis is running${NC}"

# Backend setup
echo ""
echo -e "${BLUE}Setting up backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if requirements.txt was modified or venv is new
if [ ! -f "venv/.installed" ] || [ requirements.txt -nt venv/.installed ]; then
    echo "Installing Python dependencies..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt

    # Download spaCy models
    echo "Downloading spaCy models..."
    python -m spacy download en_core_web_sm || true

    touch venv/.installed
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Backend dependencies already installed${NC}"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}Please update .env file with your configuration${NC}"
fi

# Create necessary directories
mkdir -p uploads pdfs

# Start backend in background
echo "Starting FastAPI backend on port 8000..."
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

cd ..

# Frontend setup
echo ""
echo -e "${BLUE}Setting up frontend...${NC}"
cd frontend

# Install dependencies if package.json was modified or node_modules doesn't exist
if [ ! -d "node_modules" ] || [ package.json -nt node_modules/.installed ]; then
    echo "Installing Node.js dependencies..."
    npm install
    touch node_modules/.installed
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

# Start frontend in background
echo "Starting React frontend on port 5173..."
npm run dev &
FRONTEND_PID=$!

cd ..

# Wait a bit for servers to start
sleep 3

echo ""
echo -e "${GREEN}========================================="
echo "  SmartReports is now running!"
echo "=========================================${NC}"
echo ""
echo -e "${BLUE}Frontend:${NC}  http://localhost:5173"
echo -e "${BLUE}Backend API:${NC}  http://localhost:8000"
echo -e "${BLUE}API Docs:${NC}  http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping servers...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}Servers stopped${NC}"
    exit 0
}

# Trap SIGINT and SIGTERM
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
