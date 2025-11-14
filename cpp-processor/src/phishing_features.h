#ifndef PHISHING_FEATURES_H
#define PHISHING_FEATURES_H

#include <string>
#include <vector>
#include <map>
#include <set>
#include <regex>
#include <cmath>
#include <algorithm>
#include <sstream>

/**
 * Advanced PhishGuard Feature Extraction (39 features)
 * Ported from Python for 7-12x performance improvement
 *
 * @author Matthew David Scott
 * @source ~/Projects/Security-Tools/security-phishing-detector/advanced_features.py
 */
class PhishingFeatureExtractor {
public:
    PhishingFeatureExtractor();

    // Main extraction function
    std::map<std::string, double> extractAllFeatures(const std::string& text);

    // JSON output for API responses
    std::string toJson(const std::map<std::string, double>& features);

private:
    // Keyword sets (from Python)
    std::set<std::string> urgency_words;
    std::set<std::string> financial_words;
    std::set<std::string> prize_words;
    std::set<std::string> action_words;
    std::set<std::string> url_shorteners;
    std::set<std::string> legitimate_domains;

    // Feature category extractors
    std::map<std::string, double> extractBasicStats(const std::string& text);
    std::map<std::string, double> extractKeywordFeatures(const std::string& text_lower);
    std::map<std::string, double> extractUrlFeatures(const std::string& text);
    std::map<std::string, double> extractPatternFeatures(const std::string& text);
    std::map<std::string, double> extractEntropyFeatures(const std::string& text);
    std::map<std::string, double> extractGrammarFeatures(const std::string& text);

    // Utility functions
    double calculateEntropy(const std::string& text);
    bool isTyposquatting(const std::string& url, const std::string& legitimate);
    std::vector<std::string> extractUrls(const std::string& text);
    std::string toLower(const std::string& str);
};

#endif // PHISHING_FEATURES_H
