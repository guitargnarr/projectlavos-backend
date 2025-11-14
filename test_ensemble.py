#!/usr/bin/env python3
import requests

# Test ML ensemble directly
data = {
    "features": [100,5,8,0,0,1,0,0,8080,0,1,0,4,0,0,1,0,0,0,0,0,0,0,0,0,5,0,0,0,0,3,0,0,0,0,0,0,0,0],
    "text": "URGENT: Your account will be SUSPENDED! Click http://bit.ly/verify NOW! FINAL WARNING!"
}

response = requests.post("http://localhost:9001/classify-ensemble", json=data)
result = response.json()

print(f"Risk Level: {result.get('risk_level')}")
print(f"Confidence: {result.get('confidence')}")
print(f"Risk Score: {result.get('risk_score')}")
print(f"Indicators: {result.get('indicators')}")

# Should be "Dangerous" for test to pass
if result.get('risk_level') == 'Dangerous':
    print("\n✅ WOULD PASS TEST")
else:
    print(f"\n❌ WOULD FAIL TEST (got {result.get('risk_level')})")