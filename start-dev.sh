#!/bin/bash

# Project Lavos - Start Development Environment
# Starts all 3 services and waits for health checks

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "${YELLOW}=== Starting Project Lavos Development Environment ===${NC}"
echo

# Kill any existing processes on these ports
echo "Cleaning up existing processes..."
lsof -ti:9000 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

sleep 2

# Start C++ Processor
echo "${YELLOW}Starting C++ Processor (port 9000)...${NC}"
cd cpp-processor/build
./text_processor > /tmp/lavos-cpp.log 2>&1 &
CPP_PID=$!
cd ../..

sleep 2

# Start FastAPI Backend
echo "${YELLOW}Starting FastAPI Backend (port 8000)...${NC}"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/lavos-fastapi.log 2>&1 &
FASTAPI_PID=$!

sleep 3

# Start Spring Boot Gateway
echo "${YELLOW}Starting Spring Boot Gateway (port 8080)...${NC}"
cd springboot-gateway
java -jar target/text-analysis-gateway-1.0.0.jar > /tmp/lavos-springboot.log 2>&1 &
SPRINGBOOT_PID=$!
cd ..

echo
echo "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Health checks
echo
echo "${GREEN}Checking service health...${NC}"

curl -s http://localhost:9000/health > /dev/null && echo "✓ C++ Processor: Healthy" || echo "✗ C++ Processor: Failed"
curl -s http://localhost:8000/health > /dev/null && echo "✓ FastAPI Backend: Healthy" || echo "✗ FastAPI Backend: Failed"
curl -s http://localhost:8080/api/health > /dev/null && echo "✓ Spring Boot Gateway: Healthy" || echo "✗ Spring Boot Gateway: Failed"

echo
echo "${GREEN}=== Development Environment Ready ===${NC}"
echo
echo "Services:"
echo "  C++ Processor:      http://localhost:9000 (PID: $CPP_PID)"
echo "  FastAPI Backend:    http://localhost:8000 (PID: $FASTAPI_PID)"
echo "  Spring Boot Gateway: http://localhost:8080 (PID: $SPRINGBOOT_PID)"
echo
echo "Logs:"
echo "  tail -f /tmp/lavos-cpp.log"
echo "  tail -f /tmp/lavos-fastapi.log"
echo "  tail -f /tmp/lavos-springboot.log"
echo
echo "Commands:"
echo "  ./run-tests.sh          # Run full test suite"
echo "  ./stop-dev.sh           # Stop all services"
echo "  ./benchmark-performance.sh  # Performance tests"
echo
echo "Save PIDs for cleanup:"
echo "$CPP_PID" > /tmp/lavos-cpp.pid
echo "$FASTAPI_PID" > /tmp/lavos-fastapi.pid
echo "$SPRINGBOOT_PID" > /tmp/lavos-springboot.pid
