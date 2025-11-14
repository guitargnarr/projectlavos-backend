# Platform Consolidation Plan
**Created**: 2025-11-13
**Author**: Matthew David Scott
**Status**: Phase 1 in progress

---

## Vision: Unified AI/ML Platform

**Current**: 5 isolated projects with duplicate functionality
**Target**: One Spring Boot platform serving multiple products

---

## Projects to Consolidate

### 1. ✅ **Project Lavos** (Foundation - COMPLETE)
- **Location**: `~/Projects/projectlavos-backend/`
- **Status**: Integrated with C++ + Spring Boot
- **Components**: C++ processor, Spring Boot gateway, FastAPI backend
- **Tests**: 11/11 passing
- **Performance**: 3-13x improvements verified

### 2. 🔄 **PhishGuard ML** (Phase 1 - IN PROGRESS)
- **Location**: `~/Projects/Security-Tools/security-phishing-detector/`
- **Integration Point**: Port advanced_features.py (39 features) to C++
- **Expected Gain**: 7-12x faster feature extraction (15-25ms → <2ms)
- **Complexity**: Medium (2 days effort)
- **Value**: Production-grade phishing detection for platform

### 3. ⏸️ **Mirador Core** (Phase 2 - PLANNED)
- **Location**: `~/Projects/Security-Tools/mirador-test/`
- **Integration Point**: Replace bash orchestration with Spring Boot services
- **Expected Gain**: Real multi-agent system, testable, scalable
- **Complexity**: High (3 days effort)
- **Value**: Enterprise AI orchestration, API-first design

### 4. ⏸️ **MoodScope Sentiment** (Phase 1 - PLANNED)
- **Location**: `~/Projects/AI-ML/sentiment-analysis-api/`
- **Integration Point**: Add as Python ML service for multi-language
- **Expected Gain**: 50+ language support, emotion detection
- **Complexity**: Low (1 day effort)
- **Value**: Multi-lingual sentiment for international clients

### 5. ⏸️ **Reflexia Model Manager** (Phase 2 - PLANNED)
- **Location**: `~/Projects/reflexia-model-manager/`
- **Integration Point**: Adaptive quantization for Ollama models
- **Expected Gain**: Cost optimization, intelligent model selection
- **Complexity**: Medium (2 days effort)
- **Value**: Memory-aware scaling, right-sized inference

---

## Platform Architecture (Target)

```
Spring Boot API Gateway (Port 8080)
  │
  ├─→ C++ Processing Layer (Port 9000)
  │     ├─ Text analysis ✅ DONE
  │     ├─ PhishGuard features 🔄 IN PROGRESS
  │     ├─ Basic sentiment ✅ DONE
  │     └─ Lead scoring ✅ DONE
  │
  ├─→ Python ML Layer (Port 8000-8002)
  │     ├─ FastAPI backend ✅ DONE
  │     ├─ PhishGuard ensemble ⏸️ PLANNED
  │     ├─ MoodScope transformers ⏸️ PLANNED
  │     └─ Reflexia RAG ⏸️ PLANNED
  │
  ├─→ AI Integration Layer (Ollama)
  │     ├─ Mirador agents ⏸️ PLANNED
  │     ├─ Reflexia quantization ⏸️ PLANNED
  │     └─ Multi-model orchestration ⏸️ PLANNED
  │
  └─→ Database Layer
        ├─ PostgreSQL (persistent) ⏸️ PLANNED
        ├─ Redis (caching) ⏸️ PLANNED
        └─ ChromaDB (vectors) ⏸️ PLANNED
```

---

## Phase 1: PhishGuard Integration (2 days)

### Step 1.1: Port Advanced Features to C++ (1.5 days)
**File**: `cpp-processor/src/phishing_features.cpp`

**Features to Implement**:
- Basic stats (9 features): length, word count, capital ratio, digit ratio, etc.
- Keyword features (7 features): urgency score, financial score, prize score
- URL features (7 features): shortener detection, IP addresses, suspicious TLDs, typosquatting
- Pattern features (8 features): currency detection, phone numbers, suspicious phrases
- Entropy features (8 features): character entropy, word entropy, randomness

**Reference**: `/Users/matthewscott/Projects/Security-Tools/security-phishing-detector/advanced_features.py` lines 79-230

**Expected Performance**:
- Python: 15-25ms for 39 features
- C++: <2ms for 39 features
- **Gain**: 7-12x speedup

### Step 1.2: Create Python Ensemble Service (0.5 days)
**File**: `~/Projects/projectlavos-backend/python-ml/phishing_ensemble.py`

**Copy from PhishGuard**:
- 7 trained models (Random Forest, XGBoost, LightGBM, SVM, MLP, Logistic Regression, Gradient Boosting)
- Ensemble voting logic
- FastAPI endpoint: `/classify-ensemble`

**Integration**:
- Input: 39 features from C++ layer
- Output: Ensemble prediction + individual model scores
- Cache: Redis for repeated patterns

### Step 1.3: Spring Boot Orchestration
**File**: `springboot-gateway/src/main/java/com/lavos/phishing/PhishingService.java`

**Logic**:
```java
@PostMapping("/api/phishing/classify-ensemble")
public PhishingResult classify(@RequestBody EmailRequest email) {
    // C++ extracts features (<2ms)
    List<Double> features = cppClient.extractFeatures(email);

    // Python ensemble inference (~50ms)
    EnsembleResult result = pythonMLClient.classifyEnsemble(features);

    return result;  // Total: ~52ms vs current 65-90ms
}
```

---

## Phase 2: Mirador Integration (3 days)

### Step 2.1: Replace Bash with Spring Boot (2 days)
**Current**: 97 agent patterns in bash scripts
**New**: Java service layer with agent chains

**Files to Create**:
- `AgentChainOrchestrator.java` - Routing logic
- `OllamaClient.java` - HTTP client for Ollama API
- `AgentStateManager.java` - Conversation context

**Patterns to Port**:
- Financial advisor chain: context → advisor → implementer
- Health wellness chain: context → wellness → implementer
- Music theory chain: context → theory → composition

### Step 2.2: Healthcare Cache Population (1 day)
**Current**: 1 test row (99% missing)
**Target**: 200+ real queries

**Generate**:
- Copay questions (50 queries)
- Prior authorization (50 queries)
- Eligibility (50 queries)
- Formulary (50 queries)

**Validation**: Test 70-80% cache hit rate claim

---

## Phase 3: Shared Infrastructure (1 day)

### Step 3.1: Add Redis (2 hours)
**docker-compose.yml**: Add Redis service
**Integration**: All services use same cache
**Keys**: `phishing:{hash}`, `sentiment:{hash}`, `mirador:{hash}`

### Step 3.2: Add PostgreSQL (2 hours)
**Schema**:
```sql
CREATE TABLE ml_cache (
    service VARCHAR(50),
    input_hash VARCHAR(64),
    output JSONB,
    model VARCHAR(100),
    confidence FLOAT,
    created_at TIMESTAMP
);
```

### Step 3.3: Add ChromaDB (2 hours)
**RAG Integration**:
- Store: PhishGuard training data, healthcare docs
- Query: Reflexia enhanced responses
- Share: Vectors across all projects

---

## Timeline & Effort

**Phase 1** (PhishGuard): 2 days
**Phase 2** (Mirador): 3 days
**Phase 3** (Infrastructure): 1 day
**Total**: 6 days full-time

**OR**: 2-3 weeks part-time (evenings/weekends if employed)

---

## Expected Outcomes

### Performance
- PhishGuard: 65-90ms → ~52ms (ensemble with C++ features)
- Mirador: Bash orchestration → Testable Java services
- Caching: 0% hit rate → 70-80% (Redis shared)

### Technical Debt Eliminated
- ❌ Remove: 3 duplicate sentiment implementations
- ❌ Remove: Bash orchestration (fragile)
- ❌ Remove: Separate caching per project
- ✅ Add: Single platform, shared infrastructure

### Portfolio Value
**Resume Line**:
> "Built unified AI/ML platform consolidating 5 projects into microservices architecture (C++, Java, Python). Eliminated duplicate functionality, achieved 3-13x performance improvements, 90%+ test coverage across 2,000+ lines of production code."

**Interview Answer**:
> "I had 5 separate AI/ML projects with duplicate code and no integration. I built a Spring Boot platform that consolidates everything - C++ for performance-critical features, Python for ML inference, proper orchestration. Measurable 7-12x speedups, production-ready testing, Docker deployed."

---

## Risks

**Technical**:
- Porting Python to C++ introduces bugs (mitigate: comprehensive tests)
- scikit-learn models may not load correctly (mitigate: version pinning)
- Bash → Java translation loses nuance (mitigate: preserve patterns exactly)

**Timeline**:
- 6 days full-time effort while unemployed (opportunity cost vs job search)
- IF hired at UofL: becomes 2-3 week part-time project

**Scope Creep**:
- Easy to keep adding features (mitigate: ship Phase 1, iterate)

---

## Decision Points

**NOW** (Nov 13):
- UofL interview in 6 days (Priority 1)
- This is 6-day effort (conflicts with interview prep)
- **Recommendation**: Document plan, execute AFTER interview

**Nov 20-30** (Post-Interview):
- IF hired at UofL: Execute evenings/weekends (2-3 weeks)
- IF not hired: Execute full-time (6 days)

**December**:
- Platform ready for Norton Healthcare pitch
- PhishGuard + Mirador = Enterprise AI/ML suite
- Portfolio demonstrates consolidation expertise

---

## Current Status (End of Nov 13)

**Completed Today**:
- ✅ C++ + Spring Boot + FastAPI integration
- ✅ 11/11 FastAPI tests passing
- ✅ TDD infrastructure (start-dev, run-tests, benchmarks)
- ✅ CLAUDE.md restructure (Anthropic-aligned)
- ✅ Ollama models cleaned
- ✅ PhishGuard integration researched

**Ready to Execute** (when you decide):
- Phase 1 mapped (PhishGuard C++ features)
- Phase 2 scoped (Mirador Spring Boot services)
- Phase 3 planned (shared infrastructure)

**Blocking**: Your decision on timing (before or after UofL interview)

---

**Platform exists. Integration mapped. Execution pending your go/no-go.**
