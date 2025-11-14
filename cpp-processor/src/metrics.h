#ifndef METRICS_H
#define METRICS_H

#include <atomic>
#include <chrono>
#include <sstream>
#include <string>

/**
 * Simple metrics collection for Prometheus
 * Tracks request counts, latencies, and thread pool status
 */
class Metrics {
public:
    // Request counters
    static std::atomic<long> total_requests;
    static std::atomic<long> successful_requests;
    static std::atomic<long> failed_requests;

    // Latency tracking (in microseconds)
    static std::atomic<long> total_latency_us;
    static std::atomic<long> max_latency_us;

    // Thread pool metrics
    static std::atomic<int> active_threads;
    static std::atomic<int> queued_requests;

    // Endpoint-specific counters
    static std::atomic<long> sentiment_requests;
    static std::atomic<long> phishing_requests;
    static std::atomic<long> lead_requests;

    // Generate Prometheus-format metrics
    static std::string getPrometheusMetrics() {
        std::stringstream ss;

        // Request metrics
        ss << "# HELP cpp_requests_total Total number of requests\n";
        ss << "# TYPE cpp_requests_total counter\n";
        ss << "cpp_requests_total " << total_requests.load() << "\n\n";

        ss << "# HELP cpp_requests_success Successful requests\n";
        ss << "# TYPE cpp_requests_success counter\n";
        ss << "cpp_requests_success " << successful_requests.load() << "\n\n";

        ss << "# HELP cpp_requests_failed Failed requests\n";
        ss << "# TYPE cpp_requests_failed counter\n";
        ss << "cpp_requests_failed " << failed_requests.load() << "\n\n";

        // Latency metrics
        long avg_latency = total_requests > 0 ?
            total_latency_us.load() / total_requests.load() : 0;

        ss << "# HELP cpp_latency_microseconds Request latency in microseconds\n";
        ss << "# TYPE cpp_latency_microseconds gauge\n";
        ss << "cpp_latency_microseconds{quantile=\"avg\"} " << avg_latency << "\n";
        ss << "cpp_latency_microseconds{quantile=\"max\"} " << max_latency_us.load() << "\n\n";

        // Thread pool metrics
        ss << "# HELP cpp_threadpool_active Active worker threads\n";
        ss << "# TYPE cpp_threadpool_active gauge\n";
        ss << "cpp_threadpool_active " << active_threads.load() << "\n\n";

        ss << "# HELP cpp_threadpool_queued Queued requests\n";
        ss << "# TYPE cpp_threadpool_queued gauge\n";
        ss << "cpp_threadpool_queued " << queued_requests.load() << "\n\n";

        // Endpoint metrics
        ss << "# HELP cpp_endpoint_requests Requests per endpoint\n";
        ss << "# TYPE cpp_endpoint_requests counter\n";
        ss << "cpp_endpoint_requests{endpoint=\"sentiment\"} " << sentiment_requests.load() << "\n";
        ss << "cpp_endpoint_requests{endpoint=\"phishing\"} " << phishing_requests.load() << "\n";
        ss << "cpp_endpoint_requests{endpoint=\"leads\"} " << lead_requests.load() << "\n";

        return ss.str();
    }
};

// Static member initialization
std::atomic<long> Metrics::total_requests{0};
std::atomic<long> Metrics::successful_requests{0};
std::atomic<long> Metrics::failed_requests{0};
std::atomic<long> Metrics::total_latency_us{0};
std::atomic<long> Metrics::max_latency_us{0};
std::atomic<int> Metrics::active_threads{0};
std::atomic<int> Metrics::queued_requests{0};
std::atomic<long> Metrics::sentiment_requests{0};
std::atomic<long> Metrics::phishing_requests{0};
std::atomic<long> Metrics::lead_requests{0};

#endif // METRICS_H