#!/usr/bin/env python3
"""
Benchmark: PhishGuard Feature Extraction (C++ vs Python)
Measures performance improvement from porting to C++
"""

import time
import sys
import requests
import json
from pathlib import Path

# Add PhishGuard to path
sys.path.append(str(Path.home() / "Projects" / "Security-Tools" / "security-phishing-detector"))

try:
    from advanced_features import AdvancedFeatureExtractor
except ImportError:
    print("ERROR: Could not import PhishGuard advanced_features.py")
    print("Make sure path is correct: ~/Projects/Security-Tools/security-phishing-detector/")
    sys.exit(1)

# Test emails
test_emails = [
    "URGENT! Your account has been suspended. Click here immediately to verify your identity.",
    "Dear valued customer, you have won $1,000,000! Claim your prize now at http://bit.ly/fake",
    "Your payment of $500 is overdue. Wire transfer required immediately to avoid legal action.",
    "Confirm your bank account details by clicking this link: http://paypa1-secure.tk/verify",
    "This is a legitimate email from support@github.com regarding your pull request.",
    "Hi Matthew, just following up on our meeting tomorrow. Let me know if you're still available.",
    "Your Amazon order #123456 has shipped. Track at https://amazon.com/track/abc123",
    "Download this attachment immediately - important tax refund information from IRS.",
    "Congratulations! You've been selected for a limited time offer. Act now or lose this opportunity!",
    "Reset your password here or your account will be permanently locked within 24 hours."
]

ITERATIONS = 100

print("=== PhishGuard Feature Extraction Benchmark ===")
print(f"Test emails: {len(test_emails)}")
print(f"Iterations per email: {ITERATIONS}")
print(f"Total extractions: {len(test_emails) * ITERATIONS}")
print()

# Python Baseline
print("Testing Python extraction...")
extractor_py = AdvancedFeatureExtractor()

python_times = []
for email in test_emails:
    start = time.perf_counter()
    for _ in range(ITERATIONS):
        features = extractor_py.extract_all_features(email)
    elapsed = (time.perf_counter() - start) * 1000 / ITERATIONS  # ms per extraction
    python_times.append(elapsed)

python_avg = sum(python_times) / len(python_times)
python_min = min(python_times)
python_max = max(python_times)

print(f"Python: {python_avg:.2f}ms average ({python_min:.2f}ms min, {python_max:.2f}ms max)")
print()

# C++ Comparison
print("Testing C++ extraction...")
cpp_url = "http://localhost:9000/extract-phishing-features"

cpp_times = []
for email in test_emails:
    start = time.perf_counter()
    for _ in range(ITERATIONS):
        response = requests.post(cpp_url, json={"text": email})
        if response.status_code != 200:
            print(f"ERROR: C++ endpoint returned {response.status_code}")
            sys.exit(1)
    elapsed = (time.perf_counter() - start) * 1000 / ITERATIONS  # ms per extraction
    cpp_times.append(elapsed)

cpp_avg = sum(cpp_times) / len(cpp_times)
cpp_min = min(cpp_times)
cpp_max = max(cpp_times)

print(f"C++: {cpp_avg:.2f}ms average ({cpp_min:.2f}ms min, {cpp_max:.2f}ms max)")
print()

# Results
speedup = python_avg / cpp_avg
print("=== Results ===")
print(f"Python average: {python_avg:.2f}ms")
print(f"C++ average: {cpp_avg:.2f}ms")
print(f"Speedup: {speedup:.1f}x faster")
print()

# Verify feature parity
print("Verifying feature parity...")
test_text = test_emails[0]
py_features = extractor_py.extract_all_features(test_text)
cpp_response = requests.post(cpp_url, json={"text": test_text})
cpp_features = cpp_response.json()

print(f"Python features: {len(py_features)}")
print(f"C++ features: {len(cpp_features)}")

if len(py_features) == len(cpp_features):
    print("✓ Feature count matches")
else:
    print(f"✗ Feature count MISMATCH (Python: {len(py_features)}, C++: {len(cpp_features)})")

# Check feature names match
py_keys = set(py_features.keys())
cpp_keys = set(cpp_features.keys())
missing_in_cpp = py_keys - cpp_keys
extra_in_cpp = cpp_keys - py_keys

if not missing_in_cpp and not extra_in_cpp:
    print("✓ All feature names match")
else:
    if missing_in_cpp:
        print(f"✗ Missing in C++: {missing_in_cpp}")
    if extra_in_cpp:
        print(f"✗ Extra in C++: {extra_in_cpp}")

print()
print("=== Benchmark Complete ===")
print(f"Target: 7-12x speedup")
print(f"Actual: {speedup:.1f}x speedup")
print(f"Status: {'✓ TARGET MET' if speedup >= 7 else '✗ BELOW TARGET'}")
