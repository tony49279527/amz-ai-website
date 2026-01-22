
import requests
import json
import time

url = "http://localhost:8000/api/discovery/analyze"

payload = {
    "category": "Pet Supplies",
    "keywords": "Smart Pet Water Fountain",
    "marketplace": "US",
    "reference_asins": ["B0F9FC7JYD", "B0DQ1556BW", "B0G1YB3RRC"],
    "user_name": "Tony Lee",
    "user_email": "tonylueng27149@gmail.com",
    "user_industry": "Amazon Seller",
    "user_tier": "pro"
}

print(f"Triggering analysis for: {payload['keywords']}...")
print(f"Email will be sent to: {payload['user_email']}")

try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ Request successfully received by backend.")
        print("Response:", response.json())
        print("Email should arrive shortly.")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Error: {str(e)}")
