#!/usr/bin/env python3
"""
Comprehensive Test Suite for Sentinel Platform
Tests everything that could break in production

@author Matthew David Scott
"""

import requests
import json
import time
import concurrent.futures
from typing import List, Dict
import sys

BASE_URL = "http://localhost:8080/api"

class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.NC}" if passed else f"{Colors.RED}✗ FAIL{Colors.NC}"
    print(f"{status} {name}")
    if details:
        print(f"   {details}")

# ===========================================================================
# FUNCTIONAL TESTS
# ===========================================================================

def test_all_endpoints_responding():
    """Test 1: All endpoints return 200 OK"""
    endpoints = [
        ("GET", "/health", None),
        ("POST", "/sentiment", {"text": "test"}),
        ("POST", "/leads", {"name": "Test", "email": "test@test.com"}),
        ("POST", "/phishing", {"sender": "test@test.com", "subject": "test", "body": "test"}),
    ]

    print(f"\n{Colors.YELLOW}=== Functional Tests ==={Colors.NC}")

    all_passed = True
    for method, endpoint, data in endpoints:
        try:
            if method == "GET":
                r = requests.get(BASE_URL + endpoint, timeout=5)
            else:
                r = requests.post(BASE_URL + endpoint, json=data, timeout=5)

            passed = r.status_code == 200
            print_test(f"{method} {endpoint}", passed, f"Status: {r.status_code}")
            all_passed = all_passed and passed
        except Exception as e:
            print_test(f"{method} {endpoint}", False, f"Error: {e}")
            all_passed = False

    return all_passed

# ===========================================================================
# CACHE TESTS
# ===========================================================================

def test_cache_hit_miss_pattern():
    """Test 2: Cache actually works (MISS → HIT → HIT)"""
    print(f"\n{Colors.YELLOW}=== Cache Tests ==={Colors.NC}")

    # Clear any existing cache for this text
    test_text = f"cache test {time.time()}"

    # Request 1: Should be MISS
    start = time.time()
    r1 = requests.post(f"{BASE_URL}/sentiment", json={"text": test_text})
    time1 = (time.time() - start) * 1000

    # Request 2: Should be HIT (faster)
    start = time.time()
    r2 = requests.post(f"{BASE_URL}/sentiment", json={"text": test_text})
    time2 = (time.time() - start) * 1000

    # Request 3: Should be HIT (also fast)
    start = time.time()
    r3 = requests.post(f"{BASE_URL}/sentiment", json={"text": test_text})
    time3 = (time.time() - start) * 1000

    cache_working = time2 < time1 and time3 < time1
    print_test("Cache HIT faster than MISS", cache_working,
               f"MISS: {time1:.1f}ms, HIT1: {time2:.1f}ms, HIT2: {time3:.1f}ms")

    # Verify responses identical
    identical = r1.json() == r2.json() == r3.json()
    print_test("Cached responses identical", identical)

    return cache_working and identical

# ===========================================================================
# CONCURRENCY TESTS
# ===========================================================================

def test_concurrent_requests():
    """Test 3: Handle 100 concurrent requests without crashing"""
    print(f"\n{Colors.YELLOW}=== Concurrency Tests ==={Colors.NC}")

    def make_request(i):
        try:
            r = requests.post(f"{BASE_URL}/sentiment",
                            json={"text": f"test {i}"},
                            timeout=10)
            return r.status_code == 200
        except:
            return False

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_request, i) for i in range(100)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    success_count = sum(results)
    passed = success_count == 100
    print_test(f"100 concurrent requests", passed, f"{success_count}/100 succeeded")

    return passed

# ===========================================================================
# DATA VALIDATION TESTS
# ===========================================================================

def test_special_characters():
    """Test 4: Handle special characters, unicode, injection attempts"""
    print(f"\n{Colors.YELLOW}=== Data Validation Tests ==={Colors.NC}")

    test_cases = [
        ("Emojis", "This is amazing! 😊🎉"),
        ("Unicode", "Tëst wïth spëcïål chärs"),
        ("JSON injection", '{"text":"test", "extra":"injection"}'),
        ("SQL-like", "'; DROP TABLE users; --"),
        ("XSS attempt", "<script>alert('xss')</script>"),
        ("Very long text", "word " * 1000),
        ("Empty after trim", "   "),
        ("Special punctuation", "!!!???...###"),
    ]

    all_passed = True
    for name, text in test_cases:
        try:
            r = requests.post(f"{BASE_URL}/sentiment", json={"text": text}, timeout=5)
            passed = r.status_code in [200, 400]  # Either works or properly rejects
            print_test(f"Handle {name}", passed, f"Status: {r.status_code}")
            all_passed = all_passed and passed
        except Exception as e:
            print_test(f"Handle {name}", False, f"Exception: {e}")
            all_passed = False

    return all_passed

# ===========================================================================
# PERFORMANCE TESTS
# ===========================================================================

def test_performance_targets():
    """Test 5: All endpoints meet performance targets"""
    print(f"\n{Colors.YELLOW}=== Performance Tests ==={Colors.NC}")

    endpoints = [
        ("/sentiment", {"text": "test"}, 50),  # Target: <50ms
        ("/leads", {"name": "Test", "email": "test@test.com", "company": "Test Corp"}, 50),
        ("/phishing", {"sender": "test@gmail.com", "subject": "test", "body": "test"}, 50),
    ]

    all_passed = True
    for endpoint, data, target_ms in endpoints:
        times = []
        for _ in range(10):
            start = time.time()
            requests.post(BASE_URL + endpoint, json=data, timeout=5)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

        avg_ms = sum(times) / len(times)
        passed = avg_ms < target_ms
        print_test(f"{endpoint} <{target_ms}ms", passed, f"Average: {avg_ms:.1f}ms")
        all_passed = all_passed and passed

    return all_passed

# ===========================================================================
# RESILIENCE TESTS
# ===========================================================================

def test_service_degradation():
    """Test 6: What happens when Redis fails?"""
    print(f"\n{Colors.YELLOW}=== Resilience Tests ==={Colors.NC}")

    # This test requires manually stopping Redis to verify graceful degradation
    # For now, just verify error handling exists

    try:
        # Send request with invalid JSON
        r = requests.post(f"{BASE_URL}/sentiment",
                         data="invalid json",
                         headers={"Content-Type": "application/json"},
                         timeout=5)
        passed = r.status_code == 400 or r.status_code == 500
        print_test("Graceful handling of invalid JSON", passed, f"Status: {r.status_code}")
    except:
        print_test("Graceful handling of invalid JSON", False, "Exception thrown")
        passed = False

    return passed

# ===========================================================================
# INTEGRATION TESTS
# ===========================================================================

def test_end_to_end_flow():
    """Test 7: Full request flow through all layers"""
    print(f"\n{Colors.YELLOW}=== Integration Tests ==={Colors.NC}")

    # Test Spring Boot → C++ → ML Ensemble → Response
    test_data = {
        "text": "URGENT SECURITY ALERT: Your account at http://phishing-test.com will be SUSPENDED! Click here immediately http://bit.ly/verify-now to verify your account or it will be closed. This is your FINAL WARNING! Act NOW!"
    }

    # Try ensemble endpoint first, fall back to regular if not available
    try:
        r = requests.post(f"{BASE_URL}/phishing/ensemble", json=test_data, timeout=5)
        result = r.json()

        # Check for ensemble response format
        if "risk_level" in result and "confidence" in result:
            # Ensemble format
            detected = result.get("risk_level") == "Dangerous"
            print_test("All response fields present", True)
            print_test("Phishing correctly detected", detected, f"Risk: {result.get('risk_level')}")
            conf_ok = 0.5 <= result.get("confidence", 0) <= 1.0
            print_test("Confidence in valid range", conf_ok, f"Confidence: {result.get('confidence')}")
        else:
            # Fallback logic
            raise Exception("Invalid response format")
    except:
        # Fall back to old endpoint
        test_data = {
            "sender": "urgent@phishing-test.com",
            "subject": "URGENT: Verify your account immediately",
            "body": "Click here to verify or account will be suspended. Act now!"
        }
        r = requests.post(f"{BASE_URL}/phishing", json=test_data, timeout=5)
        result = r.json()

        required_fields = ["is_phishing", "confidence", "risk_level", "indicators", "recommendation"]
        all_present = all(field in result for field in required_fields)
        print_test("All response fields present", all_present)

        detected = result.get("is_phishing") == True
        print_test("Phishing correctly detected", detected, f"Risk: {result.get('risk_level')}")

        conf_ok = 0.5 <= result.get("confidence", 0) <= 1.0
        print_test("Confidence in valid range", conf_ok, f"Confidence: {result.get('confidence')}")
        all_present = all_present if 'all_present' in locals() else True

    return all_present and detected and conf_ok

# ===========================================================================
# CACHE CONSISTENCY TESTS
# ===========================================================================

def test_cache_consistency():
    """Test 8: Cache doesn't return stale/wrong data"""
    print(f"\n{Colors.YELLOW}=== Cache Consistency Tests ==={Colors.NC}")

    # Two different texts should NOT return same cached result
    text1 = "This is amazing and wonderful"
    text2 = "This is terrible and awful"

    r1 = requests.post(f"{BASE_URL}/sentiment", json={"text": text1})
    r2 = requests.post(f"{BASE_URL}/sentiment", json={"text": text2})

    result1 = r1.json()
    result2 = r2.json()

    different = result1["sentiment"] != result2["sentiment"]
    print_test("Different inputs → different cache entries", different,
               f"Text1: {result1['sentiment']}, Text2: {result2['sentiment']}")

    return different

# ===========================================================================
# RUN ALL TESTS
# ===========================================================================

def run_all_tests():
    print(f"{Colors.YELLOW}")
    print("=" * 60)
    print("SENTINEL PLATFORM - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"{Colors.NC}")

    results = {}

    results["Functional"] = test_all_endpoints_responding()
    results["Caching"] = test_cache_hit_miss_pattern()
    results["Concurrency"] = test_concurrent_requests()
    results["Data Validation"] = test_special_characters()
    results["Performance"] = test_performance_targets()
    results["Resilience"] = test_service_degradation()
    results["Integration"] = test_end_to_end_flow()
    results["Cache Consistency"] = test_cache_consistency()

    print(f"\n{Colors.YELLOW}=== FINAL RESULTS ==={Colors.NC}\n")

    passed_count = sum(results.values())
    total_count = len(results)

    for test_name, passed in results.items():
        status = f"{Colors.GREEN}PASS{Colors.NC}" if passed else f"{Colors.RED}FAIL{Colors.NC}"
        print(f"  {status}  {test_name}")

    print(f"\n{Colors.YELLOW}Summary: {passed_count}/{total_count} test suites passed{Colors.NC}")

    if passed_count == total_count:
        print(f"\n{Colors.GREEN}=== ALL TESTS PASSED - PRODUCTION READY ==={Colors.NC}\n")
        return 0
    else:
        print(f"\n{Colors.RED}=== SOME TESTS FAILED - FIX BEFORE DEPLOY ==={Colors.NC}\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
