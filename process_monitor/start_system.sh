#!/bin/bash

# Process Monitor System Startup Script
# This script starts both the Django backend and the monitoring agent

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Process Monitor System...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if Django is installed
if ! python3 -c "import django" 2>/dev/null; then
    echo -e "${RED}❌ Django not found. Installing requirements...${NC}"
    pip install -r requirements.txt
fi

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"

    # Kill Django server
    if [ ! -z "$DJANGO_PID" ] && kill -0 "$DJANGO_PID" 2>/dev/null; then
        echo -e "${YELLOW}   Stopping Django server (PID: $DJANGO_PID)...${NC}"
        kill "$DJANGO_PID"
    fi

    # Kill monitoring agent
    if [ ! -z "$AGENT_PID" ] && kill -0 "$AGENT_PID" 2>/dev/null; then
        echo -e "${YELLOW}   Stopping monitoring agent (PID: $AGENT_PID)...${NC}"
        kill "$AGENT_PID"
    fi

    echo -e "${GREEN}✅ System shutdown complete${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start Django backend
echo -e "${YELLOW}🔧 Starting Django backend server...${NC}"
cd backend

# Run migrations
python3 manage.py migrate --run-syncdb

# Start Django server in background
python3 manage.py runserver 127.0.0.1:8000 > ../logs/django.log 2>&1 &
DJANGO_PID=$!

# Wait for Django to start
echo -e "${YELLOW}⏳ Waiting for Django server to start...${NC}"
sleep 3

# Test if Django is responding
if curl -s -f http://localhost:8000/ > /dev/null; then
    echo -e "${GREEN}✅ Django backend started successfully on http://localhost:8000/${NC}"
else
    echo -e "${RED}❌ Django backend failed to start. Check logs/django.log${NC}"
    cleanup
    exit 1
fi

# Go back to main directory
cd ..

# Start monitoring agent
echo -e "${YELLOW}📊 Starting monitoring agent...${NC}"
cd agent

# Start agent in background
python3 process_agent.py > ../logs/agent.log 2>&1 &
AGENT_PID=$!

echo -e "${GREEN}✅ Monitoring agent started (PID: $AGENT_PID)${NC}"

# Create logs directory if it doesn't exist
mkdir -p ../logs

cd ..

echo -e "${GREEN}"
echo "================================================================"
echo "🎉 Process Monitor System Started Successfully!"
echo "================================================================"
echo -e "${NC}"
echo -e "${BLUE}📊 Dashboard:${NC} http://localhost:8000/"
echo -e "${BLUE}🔧 Backend API:${NC} http://localhost:8000/api/"
echo -e "${BLUE}📁 Django Logs:${NC} logs/django.log"
echo -e "${BLUE}📁 Agent Logs:${NC} logs/agent.log"
echo ""
echo -e "${YELLOW}💡 Instructions:${NC}"
echo "   • Open http://localhost:8000/ in your browser"
echo "   • Select your host from the dropdown"
echo "   • View real-time process monitoring"
echo ""
echo -e "${YELLOW}📝 Useful commands:${NC}"
echo "   • View Django logs: tail -f logs/django.log"
echo "   • View agent logs: tail -f logs/agent.log"
echo "   • Test API: curl http://localhost:8000/api/hosts/"
echo ""
echo -e "${RED}🛑 Press Ctrl+C to stop all services${NC}"

# Wait for background processes
wait $DJANGO_PID $AGENT_PID
