#include "request_handler.h"
#include <iostream>
#include <unistd.h>
#include <cstring>
#include <sys/socket.h>
#include <map>
#include <sstream>
#include <algorithm>
#include <chrono>
#include "phishing_features.h"

// Global variables for thread synchronization
std::queue<int> g_request_queue;
pthread_mutex_t g_queue_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t g_queue_cond = PTHREAD_COND_INITIALIZER;
bool g_server_running = true;

// External functions from main.cpp (will be moved here)
extern std::map<std::string, int> analyzeWordFrequency(const std::string& text);
extern std::string buildJson(const std::map<std::string, int>& wordFreq, double sentiment, int totalWords);

// Extract JSON field from request body
std::string extractJsonField(const std::string& json, const std::string& field) {
    size_t pos = json.find("\"" + field + "\"");
    if (pos == std::string::npos) return "";

    pos = json.find(":", pos);
    if (pos == std::string::npos) return "";

    pos = json.find("\"", pos);
    if (pos == std::string::npos) return "";

    size_t endPos = json.find("\"", pos + 1);
    if (endPos == std::string::npos) return "";

    return json.substr(pos + 1, endPos - pos - 1);
}

// Calculate sentiment score
double calculateSentiment(const std::string& text) {
    int positiveWords = 0, negativeWords = 0;

    std::vector<std::string> positive = {"good", "great", "excellent", "amazing", "wonderful",
                                         "fantastic", "love", "best", "happy", "brilliant"};
    std::vector<std::string> negative = {"bad", "terrible", "awful", "horrible", "hate",
                                         "worst", "disappointing", "poor", "sad", "angry"};

    std::string lowerText = text;
    std::transform(lowerText.begin(), lowerText.end(), lowerText.begin(), ::tolower);

    for (const auto& word : positive) {
        if (lowerText.find(word) != std::string::npos) positiveWords++;
    }

    for (const auto& word : negative) {
        if (lowerText.find(word) != std::string::npos) negativeWords++;
    }

    if (positiveWords + negativeWords == 0) return 0.5;
    return (double)positiveWords / (positiveWords + negativeWords);
}

// Score lead quality
std::string scoreLead(const std::string& email, const std::string& phone,
                     const std::string& company, const std::string& budget,
                     const std::string& timeline) {
    int score = 0;
    std::string quality;
    std::vector<std::string> factors;

    // Email scoring
    if (!email.empty() && email.find("@") != std::string::npos) {
        score += 20;
        if (email.find(".com") != std::string::npos || email.find(".org") != std::string::npos) {
            score += 10;
            factors.push_back("verified_domain");
        }
        if (email.find("gmail") == std::string::npos && email.find("yahoo") == std::string::npos) {
            score += 10;
            factors.push_back("business_email");
        }
    }

    // Phone scoring
    if (!phone.empty() && phone.length() >= 10) {
        score += 15;
        factors.push_back("valid_phone");
    }

    // Company scoring
    if (!company.empty()) {
        score += 15;
        factors.push_back("company_provided");
    }

    // Budget scoring
    if (!budget.empty()) {
        score += 20;
        factors.push_back("budget_specified");
        if (budget.find("10000") != std::string::npos || budget.find("50000") != std::string::npos) {
            score += 10;
            factors.push_back("high_budget");
        }
    }

    // Timeline scoring
    if (!timeline.empty()) {
        score += 10;
        factors.push_back("timeline_provided");
        if (timeline.find("immediate") != std::string::npos || timeline.find("asap") != std::string::npos) {
            score += 10;
            factors.push_back("urgent_timeline");
        }
    }

    // Determine quality
    if (score >= 80) quality = "HOT";
    else if (score >= 60) quality = "WARM";
    else if (score >= 40) quality = "COOL";
    else quality = "COLD";

    // Build JSON response
    std::stringstream json;
    json << "{\"score\":" << score << ",\"quality\":\"" << quality << "\",\"factors\":[";
    for (size_t i = 0; i < factors.size(); i++) {
        json << "\"" << factors[i] << "\"";
        if (i < factors.size() - 1) json << ",";
    }
    json << "]}";

    return json.str();
}

// Detect phishing
std::string detectPhishing(const std::string& sender, const std::string& subject,
                          const std::string& body) {
    int riskScore = 0;
    std::vector<std::string> indicators;
    std::string riskLevel;

    // Check sender
    if (sender.find("noreply") != std::string::npos ||
        sender.find("no-reply") != std::string::npos) {
        riskScore += 15;
        indicators.push_back("suspicious_sender");
    }

    // Check subject
    std::string lowerSubject = subject;
    std::transform(lowerSubject.begin(), lowerSubject.end(), lowerSubject.begin(), ::tolower);

    if (lowerSubject.find("urgent") != std::string::npos ||
        lowerSubject.find("immediate action") != std::string::npos ||
        lowerSubject.find("verify") != std::string::npos ||
        lowerSubject.find("suspended") != std::string::npos) {
        riskScore += 25;
        indicators.push_back("urgent_language");
    }

    // Check body
    std::string lowerBody = body;
    std::transform(lowerBody.begin(), lowerBody.end(), lowerBody.begin(), ::tolower);

    if (lowerBody.find("click here") != std::string::npos ||
        lowerBody.find("verify your account") != std::string::npos ||
        lowerBody.find("suspended") != std::string::npos ||
        lowerBody.find("confirm your") != std::string::npos) {
        riskScore += 30;
        indicators.push_back("phishing_keywords");
    }

    if (lowerBody.find("http://") != std::string::npos) {
        riskScore += 20;
        indicators.push_back("suspicious_links");
    }

    // Determine risk level
    if (riskScore >= 70) riskLevel = "High";
    else if (riskScore >= 40) riskLevel = "Medium";
    else riskLevel = "Low";

    // Build JSON response
    std::stringstream json;
    json << "{\"risk_score\":" << riskScore << ",\"risk_level\":\"" << riskLevel << "\",\"indicators\":[";
    for (size_t i = 0; i < indicators.size(); i++) {
        json << "\"" << indicators[i] << "\"";
        if (i < indicators.size() - 1) json << ",";
    }
    json << "]}";

    return json.str();
}

// Worker thread function - pulls from queue and processes requests
void* worker_thread(void* arg) {
    int thread_id = *(int*)arg;
    delete (int*)arg;

    std::cout << "[Worker " << thread_id << "] Started" << std::endl;

    while (true) {
        int client_socket = -1;

        // Lock and wait for work
        pthread_mutex_lock(&g_queue_mutex);

        while (g_request_queue.empty() && g_server_running) {
            pthread_cond_wait(&g_queue_cond, &g_queue_mutex);
        }

        if (!g_server_running && g_request_queue.empty()) {
            pthread_mutex_unlock(&g_queue_mutex);
            break;
        }

        if (!g_request_queue.empty()) {
            client_socket = g_request_queue.front();
            g_request_queue.pop();
        }

        pthread_mutex_unlock(&g_queue_mutex);

        // Process request outside of lock
        if (client_socket >= 0) {
            handle_request(client_socket);
        }
    }

    std::cout << "[Worker " << thread_id << "] Exiting" << std::endl;
    return nullptr;
}

// Handle individual request
void handle_request(int client_socket) {
    // Read request
    char buffer[65536] = {0};
    ssize_t bytes_read = read(client_socket, buffer, 65536);

    if (bytes_read <= 0) {
        close(client_socket);
        return;
    }

    std::string request(buffer, bytes_read);
    std::string response = process_request(request);

    // Send response
    send(client_socket, response.c_str(), response.length(), 0);
    close(client_socket);
}

// Process request and generate response
std::string process_request(const std::string& request) {
    std::string response;

    if (request.find("GET /health") != std::string::npos) {
        // Health check
        std::string body = "{\"status\":\"healthy\",\"service\":\"cpp-processor\"}";
        response = "HTTP/1.1 200 OK\r\n"
                  "Content-Type: application/json\r\n"
                  "Content-Length: " + std::to_string(body.length()) + "\r\n"
                  "Access-Control-Allow-Origin: *\r\n\r\n" + body;
    }
    else if (request.find("POST /analyze") != std::string::npos) {
        // Extract JSON body
        size_t bodyStart = request.find("\r\n\r\n");
        std::string body = (bodyStart != std::string::npos) ? request.substr(bodyStart + 4) : "";

        // Extract text field from JSON
        std::string text = extractJsonField(body, "text");

        if (!text.empty()) {
            // Analyze text
            auto wordFreq = analyzeWordFrequency(text);
            double sentiment = calculateSentiment(text);
            int totalWords = 0;
            for (const auto& pair : wordFreq) totalWords += pair.second;

            // Build response
            std::string jsonResponse = buildJson(wordFreq, sentiment, totalWords);

            response = "HTTP/1.1 200 OK\r\n"
                      "Content-Type: application/json\r\n"
                      "Content-Length: " + std::to_string(jsonResponse.length()) + "\r\n"
                      "Access-Control-Allow-Origin: *\r\n\r\n" + jsonResponse;
        } else {
            std::string errorBody = "{\"error\":\"Missing 'text' field in request\"}";
            response = "HTTP/1.1 400 Bad Request\r\n"
                      "Content-Type: application/json\r\n"
                      "Content-Length: " + std::to_string(errorBody.length()) + "\r\n\r\n" + errorBody;
        }
    }
    else if (request.find("POST /score-lead") != std::string::npos) {
        // Extract JSON body
        size_t bodyStart = request.find("\r\n\r\n");
        std::string body = (bodyStart != std::string::npos) ? request.substr(bodyStart + 4) : "";

        // Extract fields from JSON
        std::string email = extractJsonField(body, "email");
        std::string phone = extractJsonField(body, "phone");
        std::string company = extractJsonField(body, "company");
        std::string budget = extractJsonField(body, "budget");
        std::string timeline = extractJsonField(body, "timeline");

        // Score the lead
        std::string jsonResponse = scoreLead(email, phone, company, budget, timeline);

        response = "HTTP/1.1 200 OK\r\n"
                  "Content-Type: application/json\r\n"
                  "Content-Length: " + std::to_string(jsonResponse.length()) + "\r\n"
                  "Access-Control-Allow-Origin: *\r\n\r\n" + jsonResponse;
    }
    else if (request.find("POST /detect-phishing") != std::string::npos) {
        // Extract JSON body
        size_t bodyStart = request.find("\r\n\r\n");
        std::string body = (bodyStart != std::string::npos) ? request.substr(bodyStart + 4) : "";

        // Extract fields from JSON
        std::string sender = extractJsonField(body, "sender");
        std::string subject = extractJsonField(body, "subject");
        std::string emailBody = extractJsonField(body, "body");

        // Detect phishing
        std::string jsonResponse = detectPhishing(sender, subject, emailBody);

        response = "HTTP/1.1 200 OK\r\n"
                  "Content-Type: application/json\r\n"
                  "Content-Length: " + std::to_string(jsonResponse.length()) + "\r\n"
                  "Access-Control-Allow-Origin: *\r\n\r\n" + jsonResponse;
    }
    else if (request.find("POST /extract-phishing-features") != std::string::npos) {
        // Extract JSON body
        size_t bodyStart = request.find("\r\n\r\n");
        std::string body = (bodyStart != std::string::npos) ? request.substr(bodyStart + 4) : "";

        // Extract text field from JSON
        std::string text = extractJsonField(body, "text");

        if (!text.empty()) {
            // Extract all 39 PhishGuard features with timing
            PhishingFeatureExtractor extractor;

            auto start = std::chrono::high_resolution_clock::now();
            auto features = extractor.extractAllFeatures(text);
            auto end = std::chrono::high_resolution_clock::now();

            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            double processing_time_ms = duration.count() / 1000.0;

            // Add timing to features
            features["_processing_time_ms"] = processing_time_ms;

            std::string jsonResponse = extractor.toJson(features);

            response = "HTTP/1.1 200 OK\r\n"
                      "Content-Type: application/json\r\n"
                      "Content-Length: " + std::to_string(jsonResponse.length()) + "\r\n"
                      "Access-Control-Allow-Origin: *\r\n\r\n" + jsonResponse;
        } else {
            std::string errorBody = "{\"error\":\"Missing 'text' field in request\"}";
            response = "HTTP/1.1 400 Bad Request\r\n"
                      "Content-Type: application/json\r\n"
                      "Content-Length: " + std::to_string(errorBody.length()) + "\r\n\r\n" + errorBody;
        }
    }
    else {
        std::string errorBody = "{\"error\":\"Not Found\"}";
        response = "HTTP/1.1 404 Not Found\r\n"
                  "Content-Type: application/json\r\n"
                  "Content-Length: " + std::to_string(errorBody.length()) + "\r\n\r\n" + errorBody;
    }

    return response;
}