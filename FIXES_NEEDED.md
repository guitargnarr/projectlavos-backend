# Sentinel Platform - Fixes for 8/8 Test Pass

**Current**: 6/8 test suites passing
**Target**: 8/8 for production deployment
**Status**: 2 issues identified, solutions planned

---

## Issue 1: Concurrency (98/100 Success Rate)

### Problem
- C++ server: Single-threaded accept() loop
- Under 100 concurrent requests: 2% timeout/fail
- Root cause: Sequential request handling blocks new connections

### Solution: Pthread Worker Pool

**File**: `cpp-processor/src/main.cpp`
**Implementation**: 10-thread worker pool with request queue
**Estimated time**: 1-2 hours

**Code changes**:
```cpp
#include <pthread.h>
#include <queue>

// Global request queue
std::queue<int> request_queue;
pthread_mutex_t queue_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t queue_cond = PTHREAD_COND_INITIALIZER;

void* worker_thread(void* arg) {
    while (true) {
        pthread_mutex_lock(&queue_mutex);

        // Wait for requests
        while (request_queue.empty()) {
            pthread_cond_wait(&queue_cond, &queue_mutex);
        }

        int client_socket = request_queue.front();
        request_queue.pop();
        pthread_mutex_unlock(&queue_mutex);

        // Process request (existing handle_request logic)
        handle_request(client_socket);
        close(client_socket);
    }
}

// In runServer():
// Create 10 worker threads
pthread_t threads[10];
for (int i = 0; i < 10; i++) {
    pthread_create(&threads[i], NULL, worker_thread, NULL);
}

// Accept loop adds to queue
while (true) {
    int new_socket = accept(server_fd, ...);

    pthread_mutex_lock(&queue_mutex);
    request_queue.push(new_socket);
    pthread_cond_signal(&queue_cond);
    pthread_mutex_unlock(&queue_mutex);
}
```

**Test verification**:
```bash
python3 test_comprehensive.py
# Concurrency test: Expect 100/100 success
```

---

## Issue 2: Phishing False Negative (Accuracy)

### Problem
- C++ rule-based: Conservative (confidence 0.4 for obvious phishing)
- Flagged "Suspicious" when should be "Dangerous"
- Root cause: Simple pattern matching vs trained ML models

### Solution: PhishGuard 7-Model Ensemble

**Files to create**:
1. `python-ml/phishing_service.py` (FastAPI ensemble endpoint)
2. `python-ml/models/` (copy from PhishGuard)
3. Spring Boot routing to ensemble

**Estimated time**: 3-4 hours

### Step 1: Copy Models (30 min)
```bash
mkdir -p ~/Projects/projectlavos-backend/python-ml/phishing/models
cp ~/Projects/Security-Tools/security-phishing-detector/models/*.pkl \
   ~/Projects/projectlavos-backend/python-ml/phishing/models/
```

### Step 2: Create Ensemble Service (2 hours)

**File**: `python-ml/phishing_service.py`
```python
from fastapi import FastAPI
from sklearn.ensemble import RandomForestClassifier
import joblib
import numpy as np

app = FastAPI(title="PhishGuard Ensemble Service")

class EnsembleClassifier:
    def __init__(self):
        self.models = {
            'rf': joblib.load('models/random_forest.pkl'),
            'xgb': joblib.load('models/xgboost.pkl'),
            'lgb': joblib.load('models/lightgbm.pkl'),
            'svm': joblib.load('models/svm.pkl'),
            'mlp': joblib.load('models/mlp.pkl'),
            'lr': joblib.load('models/logistic_regression.pkl'),
            'gb': joblib.load('models/gradient_boosting.pkl')
        }

    def predict(self, features: List[float]) -> Dict:
        votes = []
        confidences = []

        for name, model in self.models.items():
            pred = model.predict([features])[0]
            prob = model.predict_proba([features])[0][1]
            votes.append(pred)
            confidences.append(prob)

        ensemble_vote = np.mean(votes) > 0.5
        ensemble_conf = np.mean(confidences)

        return {
            "is_phishing": bool(ensemble_vote),
            "confidence": float(ensemble_conf),
            "risk_level": "Dangerous" if ensemble_conf > 0.7 else
                         "Suspicious" if ensemble_conf > 0.4 else "Safe",
            "models_agreed": sum(votes),
            "models_total": len(votes)
        }

ensemble = EnsembleClassifier()

@app.post("/classify-ensemble")
async def classify(request: dict):
    features = request["features"]  # 39 features from C++
    result = ensemble.predict(features)
    return result
```

### Step 3: Integrate in Spring Boot (1 hour)

**File**: `springboot-gateway/.../controller/ProjectLavosController.java`

```java
@PostMapping("/phishing/ensemble")
public ResponseEntity<?> phishingEnsemble(@RequestBody Map<String, String> request) {
    try {
        String cacheKey = request.get("sender") + ":" + request.get("subject");

        // Check cache
        var cached = cacheService.get("phishing-ensemble", cacheKey, Map.class);
        if (cached != null) return ResponseEntity.ok(cached);

        // C++ extracts 39 features (<2ms)
        String emailText = request.get("sender") + " " +
                          request.get("subject") + " " +
                          request.get("body");

        Map<String, Object> cppFeatures = cppClient.post()
            .uri("/extract-phishing-features")
            .bodyValue(Map.of("text", emailText))
            .retrieve()
            .bodyToMono(Map.class)
            .block();

        // Convert features map to array
        List<Double> featureArray = extractFeatureArray(cppFeatures);

        // Python ML ensemble (~50ms)
        Map<String, Object> ensemble = pythonMLClient.post()
            .uri("/classify-ensemble")
            .bodyValue(Map.of("features", featureArray))
            .retrieve()
            .bodyToMono(Map.class)
            .block();

        // Cache result
        cacheService.set("phishing-ensemble", cacheKey, ensemble, 86400);

        return ResponseEntity.ok(ensemble);

    } catch (Exception e) {
        return ResponseEntity.status(503).body(Map.of("error", e.getMessage()));
    }
}
```

### Step 4: Update docker-compose (15 min)

Add Python ML service:
```yaml
python-ml:
  build: ./python-ml
  ports: ["9001:9001"]
  environment:
    - REDIS_URL=redis://redis:6379
```

Update Spring Boot env:
```yaml
environment:
  - PYTHON_ML_URL=http://python-ml:9001
```

---

## Test Plan After Fixes

**Run comprehensive suite**:
```bash
./test_comprehensive.py
```

**Expected**:
- ✅ Concurrency: 100/100 (was 98/100)
- ✅ Integration: Phishing detected as "Dangerous" (was "Suspicious")
- ✅ All 8/8 suites passing

**If 8/8 passing**: Deploy to Render
**If still failing**: Debug and iterate

---

## Timeline

**Fix 1** (Concurrency): 1-2 hours
- Implement pthread pool
- Test with 100/200 concurrent
- Verify 100% success

**Fix 2** (Ensemble): 3-4 hours
- Copy models
- Create Python ML service
- Integrate with Spring Boot
- Test accuracy improvements

**Re-test**: 30 min
**Total**: 4.5-6.5 hours

---

## Current Session Summary

**Time invested**: 6+ hours
**Code written**: 4,000+ lines
**Tests passing**: 6/8 (75%)
**Performance**: 2.1-2.3ms (23x under 50ms target)

**What's working**:
- C++ performance layer (1,016 lines)
- Redis caching (verified, logs show HIT/MISS)
- Spring Boot routing (tested)
- All 6 demos functional

**What needs work**:
- Concurrency (2% failure under load)
- Phishing accuracy (ensemble vs rules)

---

**Status**: Strong foundation, 2 production issues identified, fixes planned.
**Next**: Implement pthread pool + ensemble integration → 8/8 passing → Deploy
