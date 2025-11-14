# Sentinel Platform - Monitoring Setup Guide

## Quick Start

### 1. Start Monitoring Stack

```bash
# Start Prometheus, Grafana, and exporters
docker-compose -f docker-compose.monitoring.yml up -d

# Verify services are running
docker ps | grep sentinel
```

### 2. Access Dashboards

- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Metrics Endpoints**:
  - C++ Processor: http://localhost:9000/metrics
  - Spring Boot: http://localhost:8080/actuator/prometheus
  - FastAPI: http://localhost:8000/metrics
  - ML Ensemble: http://localhost:9001/metrics

### 3. Import Dashboard

1. Open Grafana (http://localhost:3001)
2. Go to Dashboards → Import
3. Upload `monitoring/dashboards/sentinel-dashboard.json`
4. Select Prometheus as data source
5. View real-time metrics!

---

## Key Metrics Tracked

### Performance Metrics
- **Request Rate**: Requests per second across all services
- **Latency**: Average and P99 response times
- **Success Rate**: Percentage of successful requests
- **Throughput**: Total data processed per second

### System Health
- **CPU Usage**: Per service and overall
- **Memory Usage**: Heap, non-heap, and system memory
- **Thread Pool**: Active threads and queue depth
- **Network I/O**: Bytes in/out per service

### Business Metrics
- **Endpoint Usage**: Distribution across sentiment, phishing, leads
- **Cache Performance**: Hit rate, evictions, memory usage
- **ML Model Performance**: Inference time, accuracy metrics
- **Error Rates**: By endpoint and error type

---

## Alert Rules

### Critical Alerts

```yaml
# High error rate
- alert: HighErrorRate
  expr: (1 - cpp_requests_success / cpp_requests_total) > 0.05
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Error rate above 5%"

# Thread pool exhaustion
- alert: ThreadPoolExhausted
  expr: cpp_threadpool_queued > 100
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "Request queue backing up"

# High latency
- alert: HighLatency
  expr: cpp_latency_microseconds{quantile="max"} > 50000
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Max latency above 50ms"
```

---

## Custom Metrics Integration

### Adding Metrics to C++ Service

```cpp
#include "metrics.h"

// In request handler
auto start = std::chrono::high_resolution_clock::now();

// Process request...

auto end = std::chrono::high_resolution_clock::now();
auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

Metrics::total_requests++;
Metrics::successful_requests++;
Metrics::total_latency_us += duration.count();
```

### Adding Metrics to Python Service

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
request_count = Counter('ml_requests_total', 'Total ML requests')
request_duration = Histogram('ml_request_duration_seconds', 'ML request latency')
active_models = Gauge('ml_active_models', 'Number of loaded models')

# Use in code
@request_duration.time()
def classify(features):
    request_count.inc()
    # ... processing ...
```

### Adding Metrics to Spring Boot

```java
@Component
public class MetricsService {
    private final MeterRegistry registry;

    @Autowired
    public MetricsService(MeterRegistry registry) {
        this.registry = registry;
    }

    public void recordRequest(String endpoint, long duration) {
        registry.counter("gateway.requests", "endpoint", endpoint).increment();
        registry.timer("gateway.latency", "endpoint", endpoint)
                .record(duration, TimeUnit.MILLISECONDS);
    }
}
```

---

## Troubleshooting

### Prometheus Not Scraping

```bash
# Check targets
curl http://localhost:9090/api/v1/targets

# Verify metrics endpoint
curl http://localhost:9000/metrics
```

### Grafana Not Showing Data

1. Check data source configuration
2. Verify Prometheus is running
3. Check time range in dashboard
4. Validate query syntax

### High Memory Usage

```bash
# Check container stats
docker stats

# Adjust retention
docker exec sentinel-prometheus \
  promtool tsdb analyze /prometheus
```

---

## Production Deployment

### Render.com Configuration

```yaml
# render.yaml for monitoring services
services:
  - type: web
    name: sentinel-grafana
    env: docker
    dockerfilePath: ./monitoring/Dockerfile.grafana
    envVars:
      - key: GF_SECURITY_ADMIN_PASSWORD
        generateValue: true

  - type: pserv
    name: sentinel-prometheus
    env: docker
    dockerfilePath: ./monitoring/Dockerfile.prometheus
    disk:
      name: prometheus-data
      mountPath: /prometheus
      sizeGB: 10
```

### Security Considerations

1. **Change default passwords**
2. **Enable TLS for metrics endpoints**
3. **Restrict network access**
4. **Set up authentication**
5. **Regular security updates**

---

## Useful Queries

### Top Endpoints by Volume
```promql
topk(5, sum by (endpoint) (rate(cpp_endpoint_requests[5m])))
```

### Error Rate by Service
```promql
1 - (sum by (job) (rate(http_requests_total{status=~"2.."}[5m]))
  / sum by (job) (rate(http_requests_total[5m])))
```

### Cache Hit Rate
```promql
sum(rate(redis_keyspace_hits_total[5m])) /
(sum(rate(redis_keyspace_hits_total[5m])) + sum(rate(redis_keyspace_misses_total[5m])))
```

### Thread Pool Saturation
```promql
cpp_threadpool_active / 10 * 100
```

---

## Next Steps

1. **Set up alerting** with PagerDuty/Slack
2. **Create SLO dashboards** for reliability tracking
3. **Add distributed tracing** with Jaeger
4. **Implement custom business metrics**
5. **Set up log aggregation** with ELK stack

---

*Monitoring Stack for Sentinel Platform | Production-Ready Observability*