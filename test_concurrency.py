#!/usr/bin/env python3
"""Test C++ processor concurrency with pthread pool"""

import requests
import concurrent.futures
import time
import statistics

def test_request():
    """Single test request to C++ processor"""
    try:
        response = requests.post('http://localhost:8080/api/sentiment',
                                json={'text': 'This is a test message for concurrent processing'},
                                timeout=5)
        return response.status_code == 200
    except:
        return False

def run_concurrent_test(num_requests):
    """Run concurrent requests and measure success rate"""
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(test_request) for _ in range(num_requests)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    duration = time.time() - start_time
    success_count = sum(results)
    success_rate = (success_count / num_requests) * 100

    return {
        'total': num_requests,
        'success': success_count,
        'failed': num_requests - success_count,
        'success_rate': success_rate,
        'duration': duration,
        'requests_per_second': num_requests / duration
    }

def main():
    print("=== C++ Pthread Pool Concurrency Test ===\n")

    # Test with different concurrency levels
    test_levels = [10, 50, 100, 200]

    for level in test_levels:
        print(f"Testing {level} concurrent requests...")
        result = run_concurrent_test(level)

        print(f"  ✅ Success: {result['success']}/{result['total']} ({result['success_rate']:.1f}%)")
        print(f"  ⏱️  Duration: {result['duration']:.2f}s")
        print(f"  📊 Rate: {result['requests_per_second']:.1f} req/s")

        if result['success_rate'] < 100:
            print(f"  ⚠️  Failed: {result['failed']} requests")

        print()

    # Final test: 100 requests (target for fix)
    print("📋 Final Test: 100 Concurrent Requests")
    print("-" * 40)
    final_result = run_concurrent_test(100)

    if final_result['success_rate'] == 100:
        print(f"✅ SUCCESS: {final_result['success']}/100 requests succeeded!")
        print(f"🎯 Pthread pool fix VERIFIED - 100% concurrency achieved")
    else:
        print(f"❌ FAILURE: Only {final_result['success']}/100 succeeded")
        print(f"   {final_result['failed']} requests failed")

    return final_result['success_rate'] == 100

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)