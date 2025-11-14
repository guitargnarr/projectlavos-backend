#ifndef REQUEST_HANDLER_H
#define REQUEST_HANDLER_H

#include <string>
#include <pthread.h>
#include <queue>
#include "phishing_features.h"

/**
 * Thread-safe Request Handler for Sentinel Platform
 * Implements worker pool pattern for concurrent request processing
 *
 * @author Matthew David Scott
 */

// Global request queue and synchronization
extern std::queue<int> g_request_queue;
extern pthread_mutex_t g_queue_mutex;
extern pthread_cond_t g_queue_cond;
extern bool g_server_running;

// Request handling functions
void* worker_thread(void* arg);
void handle_request(int client_socket);
std::string process_request(const std::string& request);

// Utility functions (from main.cpp)
std::string extractJsonField(const std::string& json, const std::string& field);
double calculateSentiment(const std::string& text);
std::string scoreLead(const std::string& email, const std::string& phone,
                      const std::string& company, const std::string& budget,
                      const std::string& timeline);
std::string detectPhishing(const std::string& sender, const std::string& subject,
                           const std::string& body);

#endif // REQUEST_HANDLER_H
