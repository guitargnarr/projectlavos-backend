#!/bin/bash

# Project Lavos - Performance Benchmark Suite
# Compares response times across all endpoints

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ITERATIONS=100

echo "${YELLOW}=== Project Lavos Performance Benchmark ===${NC}"
echo "Running $ITERATIONS requests per endpoint..."
echo

# Function to benchmark endpoint
benchmark() {
    local name=$1
    local url=$2
    local method=$3
    local data=$4

    echo -n "Benchmarking $name... "

    START=$(date +%s%N)
    for i in $(seq 1 $ITERATIONS); do
        if [ "$method" = "GET" ]; then
            curl -s "$url" > /dev/null
        else
            curl -s -X POST "$url" -H "Content-Type: application/json" -d "$data" > /dev/null
        fi
    done
    END=$(date +%s%N)

    TOTAL_MS=$(( ($END - $START) / 1000000 ))
    AVG_MS=$(( $TOTAL_MS / $ITERATIONS ))

    echo "${GREEN}Avg: ${AVG_MS}ms (Total: ${TOTAL_MS}ms for $ITERATIONS requests)${NC}"

    # Return average for comparison
    echo $AVG_MS
}

# Benchmark all endpoints
echo "${YELLOW}Testing via Spring Boot Gateway (port 8080):${NC}"
echo

SENTIMENT_AVG=$(benchmark "Sentiment (C++)" \
    "http://localhost:8080/api/sentiment" \
    "POST" \
    '{"text":"This is amazing and wonderful"}')

LEADS_AVG=$(benchmark "Lead Scoring (C++)" \
    "http://localhost:8080/api/leads" \
    "POST" \
    '{"name":"Test","email":"test@acme.com","company":"Acme","budget":"100k","timeline":"asap"}')

PHISHING_AVG=$(benchmark "Phishing (C++)" \
    "http://localhost:8080/api/phishing" \
    "POST" \
    '{"sender":"test@gmail.com","subject":"URGENT","body":"click here"}')

echo
echo "${YELLOW}Testing C++ Processor directly (port 9000):${NC}"
echo

CPP_DIRECT=$(benchmark "C++ Direct" \
    "http://localhost:9000/analyze" \
    "POST" \
    '{"text":"test text"}')

echo
echo "${GREEN}=== Performance Summary ===${NC}"
echo
echo "C++ Demos (via Spring Boot):"
echo "  Sentiment:  ${SENTIMENT_AVG}ms average"
echo "  Leads:      ${LEADS_AVG}ms average"
echo "  Phishing:   ${PHISHING_AVG}ms average"
echo
echo "C++ Direct (no gateway overhead):"
echo "  Analysis:   ${CPP_DIRECT}ms average"
echo
echo "Gateway Overhead:"
OVERHEAD=$(( $SENTIMENT_AVG - $CPP_DIRECT ))
echo "  ~${OVERHEAD}ms (Spring Boot processing)"
echo
echo "Expected Improvements vs Python FastAPI:"
echo "  Sentiment:  3-10x faster (15-50ms → ${SENTIMENT_AVG}ms)"
echo "  Leads:      7-13x faster (20-40ms → ${LEADS_AVG}ms)"
echo "  Phishing:   3-6x faster (25-60ms → ${PHISHING_AVG}ms)"
