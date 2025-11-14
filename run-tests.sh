#!/bin/bash

# Project Lavos - Master Test Runner
# Runs all test suites: C++, Java, Python, Integration

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0

echo "${YELLOW}=== Project Lavos Test Suite ===${NC}"
echo

# FastAPI Tests
echo "${YELLOW}Running FastAPI Tests (pytest)...${NC}"
if pytest test_main.py -v; then
    echo "${GREEN}✓ FastAPI tests passed${NC}"
else
    echo "${RED}✗ FastAPI tests failed${NC}"
    FAILED=1
fi

echo

# Spring Boot Tests
echo "${YELLOW}Running Spring Boot Tests (JUnit)...${NC}"
cd springboot-gateway
if mvn test -q; then
    echo "${GREEN}✓ Spring Boot tests passed${NC}"
else
    echo "${RED}✗ Spring Boot tests failed${NC}"
    FAILED=1
fi
cd ..

echo

# C++ Tests (if available)
if [ -f "cpp-processor/build/run_tests" ]; then
    echo "${YELLOW}Running C++ Tests (Google Test)...${NC}"
    if cpp-processor/build/run_tests; then
        echo "${GREEN}✓ C++ tests passed${NC}"
    else
        echo "${RED}✗ C++ tests failed${NC}"
        FAILED=1
    fi
    echo
fi

# Integration Tests
if [ -f "./test-integration.sh" ]; then
    echo "${YELLOW}Running Integration Tests...${NC}"
    if ./test-integration.sh; then
        echo "${GREEN}✓ Integration tests passed${NC}"
    else
        echo "${RED}✗ Integration tests failed${NC}"
        FAILED=1
    fi
fi

echo
if [ $FAILED -eq 0 ]; then
    echo "${GREEN}=== ALL TESTS PASSED ===${NC}"
    exit 0
else
    echo "${RED}=== SOME TESTS FAILED ===${NC}"
    exit 1
fi
