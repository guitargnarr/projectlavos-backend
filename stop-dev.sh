#!/bin/bash

# Project Lavos - Stop Development Environment
# Gracefully shuts down all services

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "${YELLOW}=== Stopping Project Lavos Development Environment ===${NC}"
echo

# Kill by PID if available
if [ -f /tmp/lavos-cpp.pid ]; then
    PID=$(cat /tmp/lavos-cpp.pid)
    kill $PID 2>/dev/null && echo "✓ Stopped C++ Processor (PID: $PID)" || echo "✗ C++ already stopped"
    rm /tmp/lavos-cpp.pid
fi

if [ -f /tmp/lavos-fastapi.pid ]; then
    PID=$(cat /tmp/lavos-fastapi.pid)
    kill $PID 2>/dev/null && echo "✓ Stopped FastAPI Backend (PID: $PID)" || echo "✗ FastAPI already stopped"
    rm /tmp/lavos-fastapi.pid
fi

if [ -f /tmp/lavos-springboot.pid ]; then
    PID=$(cat /tmp/lavos-springboot.pid)
    kill $PID 2>/dev/null && echo "✓ Stopped Spring Boot Gateway (PID: $PID)" || echo "✗ Spring Boot already stopped"
    rm /tmp/lavos-springboot.pid
fi

# Fallback: Kill by port
lsof -ti:9000 | xargs kill -9 2>/dev/null && echo "✓ Freed port 9000" || true
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✓ Freed port 8000" || true
lsof -ti:8080 | xargs kill -9 2>/dev/null && echo "✓ Freed port 8080" || true

echo
echo "${GREEN}All services stopped.${NC}"
