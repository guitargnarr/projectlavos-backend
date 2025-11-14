#include "phishing_features.h"
#include <cctype>
#include <unordered_map>

// Constructor - Initialize keyword sets from Python reference
PhishingFeatureExtractor::PhishingFeatureExtractor() {
    // Urgency words (from Python lines 18-22)
    urgency_words = {
        "urgent", "immediate", "expires", "suspended", "locked",
        "verify", "confirm", "update", "act now", "limited time",
        "final notice", "warning", "alert", "attention required"
    };

    // Financial words (from Python lines 24-28)
    financial_words = {
        "payment", "invoice", "refund", "tax", "irs", "bank",
        "account", "billing", "credit", "debit", "transaction",
        "transfer", "wire", "deposit", "withdrawal"
    };

    // Prize words (from Python lines 30-33)
    prize_words = {
        "congratulations", "winner", "won", "prize", "lottery",
        "jackpot", "million", "claim", "selected", "lucky"
    };

    // Action words (from Python lines 35-38)
    action_words = {
        "click", "download", "install", "open", "view",
        "access", "login", "sign", "enter", "submit"
    };

    // URL shorteners (from Python lines 41-44)
    url_shorteners = {
        "bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "is.gd",
        "buff.ly", "short.link", "tiny.cc", "shorturl.at"
    };

    // Legitimate domains (from Python lines 47-51)
    legitimate_domains = {
        "google.com", "gmail.com", "apple.com", "microsoft.com",
        "amazon.com", "paypal.com", "ebay.com", "facebook.com",
        "twitter.com", "linkedin.com", "youtube.com", "instagram.com"
    };
}

// Main extraction function (from Python lines 53-77)
std::map<std::string, double> PhishingFeatureExtractor::extractAllFeatures(const std::string& text) {
    std::map<std::string, double> features;
    std::string text_lower = toLower(text);

    // Extract all feature categories
    auto basic = extractBasicStats(text);
    auto keywords = extractKeywordFeatures(text_lower);
    auto urls = extractUrlFeatures(text);
    auto patterns = extractPatternFeatures(text);
    auto entropy = extractEntropyFeatures(text);
    auto grammar = extractGrammarFeatures(text);

    // Merge all features
    features.insert(basic.begin(), basic.end());
    features.insert(keywords.begin(), keywords.end());
    features.insert(urls.begin(), urls.end());
    features.insert(patterns.begin(), patterns.end());
    features.insert(entropy.begin(), entropy.end());
    features.insert(grammar.begin(), grammar.end());

    return features;
}

// Basic Statistics (from Python lines 79-91) - 9 features
std::map<std::string, double> PhishingFeatureExtractor::extractBasicStats(const std::string& text) {
    std::map<std::string, double> features;

    features["length"] = text.length();

    // Count words (split by whitespace)
    std::istringstream iss(text);
    int num_words = 0;
    std::string word;
    while (iss >> word) num_words++;
    features["num_words"] = num_words;

    // Count sentences (. ! ?)
    features["num_sentences"] = std::count(text.begin(), text.end(), '.') +
                                std::count(text.begin(), text.end(), '!') +
                                std::count(text.begin(), text.end(), '?');

    // Count capitals
    int num_capitals = 0;
    for (char c : text) {
        if (std::isupper(c)) num_capitals++;
    }
    features["num_capitals"] = num_capitals;
    features["capital_ratio"] = num_capitals / std::max(1.0, static_cast<double>(text.length()));

    // Count digits
    int num_digits = 0;
    for (char c : text) {
        if (std::isdigit(c)) num_digits++;
    }
    features["num_digits"] = num_digits;
    features["digit_ratio"] = num_digits / std::max(1.0, static_cast<double>(text.length()));

    // Count special characters
    std::string special_chars = "!@#$%^&*()";
    int num_special = 0;
    for (char c : text) {
        if (special_chars.find(c) != std::string::npos) num_special++;
    }
    features["num_special"] = num_special;
    features["special_ratio"] = num_special / std::max(1.0, static_cast<double>(text.length()));

    return features;
}

// Keyword Features (from Python lines 93-111) - 7 features
std::map<std::string, double> PhishingFeatureExtractor::extractKeywordFeatures(const std::string& text_lower) {
    std::map<std::string, double> features;

    // Count words in each category
    features["urgency_score"] = 0;
    for (const auto& word : urgency_words) {
        if (text_lower.find(word) != std::string::npos) features["urgency_score"]++;
    }

    features["financial_score"] = 0;
    for (const auto& word : financial_words) {
        if (text_lower.find(word) != std::string::npos) features["financial_score"]++;
    }

    features["prize_score"] = 0;
    for (const auto& word : prize_words) {
        if (text_lower.find(word) != std::string::npos) features["prize_score"]++;
    }

    features["action_score"] = 0;
    for (const auto& word : action_words) {
        if (text_lower.find(word) != std::string::npos) features["action_score"]++;
    }

    // Check for ALL CAPS urgency (from Python lines 103-105)
    features["has_caps_urgency"] = 0.0;
    for (const auto& word : urgency_words) {
        std::string upper_word = word;
        std::transform(upper_word.begin(), upper_word.end(), upper_word.begin(), ::toupper);
        if (text_lower.find(upper_word) != std::string::npos) {
            features["has_caps_urgency"] = 1.0;
            break;
        }
    }

    // Multiple exclamation marks (from Python lines 108-109)
    features["multiple_exclamation"] = (text_lower.find("!!") != std::string::npos) ? 1.0 : 0.0;
    features["exclamation_count"] = std::count(text_lower.begin(), text_lower.end(), '!');

    return features;
}

// Pattern Features (from Python lines 184-220) - 8 features
std::map<std::string, double> PhishingFeatureExtractor::extractPatternFeatures(const std::string& text) {
    std::map<std::string, double> features;

    // Currency detection (from Python lines 189-191)
    std::regex currency_regex(R"(\$[\d,]+\.?\d*|\d+\s*(USD|dollars?|euros?|pounds?|GBP|EUR))",
                             std::regex::icase);
    auto currency_begin = std::sregex_iterator(text.begin(), text.end(), currency_regex);
    auto currency_end = std::sregex_iterator();
    int currency_count = std::distance(currency_begin, currency_end);

    features["has_currency"] = (currency_count > 0) ? 1.0 : 0.0;
    features["currency_count"] = currency_count;

    // Phone number detection (from Python lines 193-195)
    std::regex phone_regex(R"(\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b|\b\d{10}\b)");
    features["has_phone"] = std::regex_search(text, phone_regex) ? 1.0 : 0.0;

    // Email detection (from Python lines 197-199)
    std::regex email_regex(R"(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)");
    auto email_begin = std::sregex_iterator(text.begin(), text.end(), email_regex);
    auto email_end = std::sregex_iterator();
    features["num_emails"] = std::distance(email_begin, email_end);

    // Suspicious phrases (from Python lines 202-218)
    std::vector<std::string> suspicious_phrases = {
        "verify your account", "suspended account", "click here immediately",
        "confirm your identity", "update your information", "claim your prize",
        "act now", "limited time offer", "this is not a scam",
        "dear customer", "valued customer"
    };

    std::string text_lower = toLower(text);
    int phrase_count = 0;
    for (const auto& phrase : suspicious_phrases) {
        if (text_lower.find(phrase) != std::string::npos) phrase_count++;
    }
    features["suspicious_phrase_count"] = phrase_count;

    return features;
}

// Entropy Features (from Python lines 222-241) - 8 features
std::map<std::string, double> PhishingFeatureExtractor::extractEntropyFeatures(const std::string& text) {
    std::map<std::string, double> features;

    // Character entropy (from Python lines 227)
    features["char_entropy"] = calculateEntropy(text);

    // Word entropy (from Python lines 230-231)
    std::istringstream iss(toLower(text));
    std::string words_joined;
    std::string word;
    while (iss >> word) {
        words_joined += word + " ";
    }
    features["word_entropy"] = calculateEntropy(words_joined);

    // Punctuation density (from Python lines 234-235)
    int punct_count = 0;
    for (char c : text) {
        if (std::ispunct(c)) punct_count++;
    }
    features["punctuation_density"] = punct_count / std::max(1.0, static_cast<double>(text.length()));

    // Whitespace irregularity (from Python lines 238-239)
    features["multiple_spaces"] = (text.find("  ") != std::string::npos) ? 1.0 : 0.0;
    features["space_ratio"] = std::count(text.begin(), text.end(), ' ') / std::max(1.0, static_cast<double>(text.length()));

    return features;
}

// Shannon Entropy Calculation (from Python lines 243-259)
double PhishingFeatureExtractor::calculateEntropy(const std::string& text) {
    if (text.empty()) return 0.0;

    // Count character frequencies
    std::unordered_map<char, int> char_counts;
    for (char c : text) {
        char_counts[c]++;
    }

    // Calculate entropy
    double entropy = 0.0;
    double length = text.length();

    for (const auto& pair : char_counts) {
        double probability = pair.second / length;
        if (probability > 0) {
            entropy -= probability * std::log2(probability);
        }
    }

    return entropy;
}

// Grammar Features (from Python lines 261-297) - 6 features
std::map<std::string, double> PhishingFeatureExtractor::extractGrammarFeatures(const std::string& text) {
    std::map<std::string, double> features;

    // Average word length (from Python lines 266-270)
    std::istringstream iss(text);
    std::vector<std::string> words;
    std::string word;
    while (iss >> word) {
        words.push_back(word);
    }

    if (!words.empty()) {
        double total_length = 0;
        for (const auto& w : words) {
            total_length += w.length();
        }
        features["avg_word_length"] = total_length / words.size();
    } else {
        features["avg_word_length"] = 0.0;
    }

    // Sentence length analysis (from Python lines 273-286)
    std::regex sentence_splitter(R"([.!?]+)");
    std::vector<std::string> sentences;
    std::sregex_token_iterator iter(text.begin(), text.end(), sentence_splitter, -1);
    std::sregex_token_iterator end;

    std::vector<int> sentence_lengths;
    for (; iter != end; ++iter) {
        std::string sentence = iter->str();
        if (!sentence.empty() && sentence.find_first_not_of(" \t\n\r") != std::string::npos) {
            std::istringstream sent_stream(sentence);
            int word_count = 0;
            std::string w;
            while (sent_stream >> w) word_count++;
            if (word_count > 0) sentence_lengths.push_back(word_count);
        }
    }

    if (!sentence_lengths.empty()) {
        double sum = 0;
        for (int len : sentence_lengths) sum += len;
        double mean = sum / sentence_lengths.size();
        features["avg_sentence_length"] = mean;

        // Variance calculation (from Python lines 280-281)
        if (sentence_lengths.size() > 1) {
            double variance_sum = 0;
            for (int len : sentence_lengths) {
                variance_sum += (len - mean) * (len - mean);
            }
            features["sentence_length_variance"] = variance_sum / sentence_lengths.size();
        } else {
            features["sentence_length_variance"] = 0.0;
        }
    } else {
        features["avg_sentence_length"] = 0.0;
        features["sentence_length_variance"] = 0.0;
    }

    // Question marks (from Python lines 289-290)
    features["num_questions"] = std::count(text.begin(), text.end(), '?');
    int num_sentences = std::max(1, static_cast<int>(sentence_lengths.size()));
    features["question_ratio"] = features["num_questions"] / num_sentences;

    // Repeated punctuation (from Python lines 293-295)
    features["repeated_punctuation"] = 0.0;
    if (text.find("!!") != std::string::npos ||
        text.find("??") != std::string::npos ||
        text.find("..") != std::string::npos) {
        features["repeated_punctuation"] = 1.0;
    }

    return features;
}

// URL Features (from Python lines 113-159) - 7 features
std::map<std::string, double> PhishingFeatureExtractor::extractUrlFeatures(const std::string& text) {
    std::map<std::string, double> features;

    // Extract URLs with regex (from Python line 116)
    auto urls = extractUrls(text);

    // Initialize features
    features["num_urls"] = urls.size();
    features["has_url"] = urls.empty() ? 0.0 : 1.0;
    features["has_shortener"] = 0.0;
    features["has_ip_address"] = 0.0;
    features["suspicious_tld"] = 0.0;
    features["typosquatting_risk"] = 0.0;
    features["url_entropy_avg"] = 0.0;

    if (urls.empty()) return features;

    // Analyze each URL
    std::vector<double> entropy_scores;
    std::regex ip_pattern(R"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})");
    std::vector<std::string> suspicious_tlds = {".tk", ".ml", ".ga", ".cf", ".click", ".download"};

    for (const auto& url : urls) {
        std::string url_lower = toLower(url);

        // Check for URL shorteners (from Python lines 136-137)
        for (const auto& shortener : url_shorteners) {
            if (url_lower.find(shortener) != std::string::npos) {
                features["has_shortener"] = 1.0;
                break;
            }
        }

        // Check for IP addresses (from Python lines 140-142)
        if (std::regex_search(url, ip_pattern)) {
            features["has_ip_address"] = 1.0;
        }

        // Check for suspicious TLDs (from Python lines 145-147)
        for (const auto& tld : suspicious_tlds) {
            if (url_lower.find(tld) != std::string::npos) {
                features["suspicious_tld"] = 1.0;
                break;
            }
        }

        // Check for typosquatting (from Python lines 150-152)
        for (const auto& legit : legitimate_domains) {
            if (isTyposquatting(url_lower, legit)) {
                features["typosquatting_risk"] = 1.0;
                break;
            }
        }

        // Calculate URL entropy (from Python line 155)
        entropy_scores.push_back(calculateEntropy(url));
    }

    // Average URL entropy (from Python line 157)
    if (!entropy_scores.empty()) {
        double sum = 0;
        for (double e : entropy_scores) sum += e;
        features["url_entropy_avg"] = sum / entropy_scores.size();
    }

    return features;
}

// Extract URLs from text (utility)
std::vector<std::string> PhishingFeatureExtractor::extractUrls(const std::string& text) {
    std::vector<std::string> urls;
    std::regex url_pattern(R"(https?://[^\s<>"{}|\\^`\[\]]+)", std::regex::icase);

    auto begin = std::sregex_iterator(text.begin(), text.end(), url_pattern);
    auto end = std::sregex_iterator();

    for (std::sregex_iterator i = begin; i != end; ++i) {
        urls.push_back(i->str());
    }

    return urls;
}

// Typosquatting detection (from Python lines 161-182)
bool PhishingFeatureExtractor::isTyposquatting(const std::string& url, const std::string& legitimate) {
    // Common typosquatting patterns (from Python lines 164-172)
    std::vector<std::string> typo_patterns;
    std::string temp;

    temp = legitimate; std::replace(temp.begin(), temp.end(), 'a', '4'); typo_patterns.push_back(temp);
    temp = legitimate; std::replace(temp.begin(), temp.end(), 'e', '3'); typo_patterns.push_back(temp);
    temp = legitimate; std::replace(temp.begin(), temp.end(), 'i', '1'); typo_patterns.push_back(temp);
    temp = legitimate; std::replace(temp.begin(), temp.end(), 'o', '0'); typo_patterns.push_back(temp);
    temp = legitimate; std::replace(temp.begin(), temp.end(), 's', '5'); typo_patterns.push_back(temp);

    // Check each pattern
    for (const auto& pattern : typo_patterns) {
        if (url.find(pattern) != std::string::npos && url.find(legitimate) == std::string::npos) {
            return true;
        }
    }

    // Check for extra characters (from Python lines 179-180)
    if (legitimate.length() > 4) {
        std::string base = legitimate.substr(0, legitimate.length() - 4); // Remove .com
        if (url.find(base) != std::string::npos && url.find(legitimate) == std::string::npos) {
            return true;
        }
    }

    return false;
}

// Utility: Convert to lowercase
std::string PhishingFeatureExtractor::toLower(const std::string& str) {
    std::string result = str;
    std::transform(result.begin(), result.end(), result.begin(), ::tolower);
    return result;
}

// JSON output for API responses
std::string PhishingFeatureExtractor::toJson(const std::map<std::string, double>& features) {
    std::stringstream ss;
    ss << "{";

    bool first = true;
    for (const auto& pair : features) {
        if (!first) ss << ",";
        ss << "\"" << pair.first << "\":" << pair.second;
        first = false;
    }

    ss << "}";
    return ss.str();
}
