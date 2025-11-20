# Project Lavos - AI/ML Platform Backend

## Platform Architecture (Updated: 2025-11-13)

**3-Service Microservices**:
```
Spring Boot Gateway (8080)
  ├─→ C++ Processor (9000) - Performance layer
  │     ├─ Sentiment (<5ms)
  │     ├─ Lead scoring (<3ms)
  │     ├─ Phishing detection (<10ms)
  │     └─ PhishGuard features (39 features, <2ms)
  │
  ├─→ FastAPI Backend (8000) - AI integration
  │     ├─ Restaurant analyzer (Claude)
  │     ├─ Email scorer (Claude)
  │     └─ Prompt engineering (Claude)
  │
  └─→ Redis (6379) - Shared caching
        ├─ Sentiment cache (1 hour TTL)
        ├─ Phishing patterns (24 hours TTL)
        └─ Lead scores (24 hours TTL)
```

## Development Workflow

```bash
# Start all services
./start-dev.sh

# Run tests (11/11 FastAPI, 5 Spring Boot)
./run-tests.sh

# Benchmark performance
./benchmark-performance.sh

# Stop services
./stop-dev.sh
```

## C++ Endpoints (Port 9000)

- POST /analyze - Word frequency + sentiment
- POST /score-lead - Lead qualification scoring
- POST /detect-phishing - Simple rule-based phishing
- POST /extract-phishing-features - 39 advanced features (PhishGuard)
- GET /health - Health check

## Redis Caching

**Cache keys**: `{service}:{sha256(input)[:16]}`
**Services using cache**: sentiment, leads, phishing
**Hit rate target**: 70%+
**Stats endpoint**: GET /api/cache/stats

## Critical Rules

- Test before commit: `./run-tests.sh`
- Performance regression: Run benchmarks
- Cache invalidation: 1 hour (sentiment), 24 hours (patterns)

## Recent Additions (Day 1 - Nov 13)

- ✅ PhishGuard 39 features ported to C++ (320 lines)
- ✅ Redis caching integrated (FastAPI complete, Spring Boot pending)
- ✅ 1,016 lines C++ written
- ✅ 50% cache hit rate verified

## Documentation References

- Memory system: @~/.claude/archive/SYSTEM_DOCUMENTATION.md
- Optimal workflows: @~/.claude/archive/WORKFLOWS.md
