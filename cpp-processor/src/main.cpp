#include <iostream>
#include <string>
#include <map>
#include <sstream>
#include <algorithm>
#include <cctype>
#include <vector>
#include <cmath>
#include <iomanip>

// Lightweight HTTP server - using raw sockets for simplicity
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <cstring>

// PhishGuard advanced feature extraction
#include "phishing_features.h"

// Thread pool for concurrent request handling
#include <pthread.h>
#include "request_handler.h"

// Simple JSON builder (minimal implementation)
std::string buildJson(const std::map<std::string, int>& wordFreq, double sentiment, int totalWords) {
    std::stringstream ss;
    ss << "{";
    ss << "\"totalWords\":" << totalWords << ",";
    ss << "\"uniqueWords\":" << wordFreq.size() << ",";
    ss << "\"sentiment\":" << sentiment << ",";
    ss << "\"topWords\":[";

    // Get top 10 words
    std::vector<std::pair<std::string, int>> sortedWords(wordFreq.begin(), wordFreq.end());
    std::sort(sortedWords.begin(), sortedWords.end(),
              [](const auto& a, const auto& b) { return a.second > b.second; });

    for (size_t i = 0; i < std::min(size_t(10), sortedWords.size()); ++i) {
        if (i > 0) ss << ",";
        ss << "{\"word\":\"" << sortedWords[i].first << "\",\"count\":" << sortedWords[i].second << "}";
    }

    ss << "]}";
    return ss.str();
}

// Analyze word frequency in text
std::map<std::string, int> analyzeWordFrequency(const std::string& text) {
    std::map<std::string, int> frequency;
    std::stringstream ss(text);
    std::string word;

    while (ss >> word) {
        // Clean word (remove punctuation, lowercase)
        word.erase(std::remove_if(word.begin(), word.end(),
                   [](char c) { return !std::isalnum(c); }), word.end());
        std::transform(word.begin(), word.end(), word.begin(), ::tolower);

        if (!word.empty()) {
            frequency[word]++;
        }
    }

    return frequency;
}

// HTTP server
void runServer(int port) {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);

    // Create socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        std::cerr << "Socket creation failed" << std::endl;
        exit(EXIT_FAILURE);
    }

    // Set socket options (macOS compatible)
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))) {
        std::cerr << "Setsockopt SO_REUSEADDR failed" << std::endl;
        exit(EXIT_FAILURE);
    }
    #ifdef SO_REUSEPORT
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt)); // Optional on macOS
    #endif

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port);

    // Bind socket
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        std::cerr << "Bind failed on port " << port << std::endl;
        exit(EXIT_FAILURE);
    }

    // Listen with increased backlog for concurrent connections
    if (listen(server_fd, 100) < 0) {
        std::cerr << "Listen failed" << std::endl;
        exit(EXIT_FAILURE);
    }

    std::cout << "C++ Text Processor running on port " << port << std::endl;

    // Create worker thread pool
    pthread_t workers[10];
    for (int i = 0; i < 10; i++) {
        int* thread_id = new int(i);
        if (pthread_create(&workers[i], nullptr, worker_thread, thread_id) != 0) {
            std::cerr << "Failed to create worker thread " << i << std::endl;
        }
    }
    std::cout << "Created 10 worker threads for concurrent processing" << std::endl;
    std::cout << "Endpoints: POST /analyze, POST /score-lead, POST /detect-phishing, POST /extract-phishing-features, GET /health" << std::endl;

    while (true) {
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
            std::cerr << "Accept failed" << std::endl;
            continue;
        }

        // Add to queue for worker threads instead of processing inline
        pthread_mutex_lock(&g_queue_mutex);
        g_request_queue.push(new_socket);
        pthread_cond_signal(&g_queue_cond);
        pthread_mutex_unlock(&g_queue_mutex);
    }

    close(server_fd);
}

int main() {
    std::cout << "=== C++ High-Performance Text Processor ===" << std::endl;
    std::cout << "Author: Matthew David Scott" << std::endl;
    std::cout << "Tech: C++17, Raw Sockets, Zero Dependencies" << std::endl;
    std::cout << std::endl;

    runServer(9000);
    return 0;
}
