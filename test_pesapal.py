#!/usr/bin/env python3
"""
Test script for PesaPal integration debugging
Run this script to test your PesaPal configuration and API calls
"""

import requests
import json
import sys

# Configuration - update these with your actual values
BASE_URL = "http://localhost:5000"  # Change to your server URL
PESAPAL_BASE_URL = "https://cybqa.pesapal.com"  # Change to your PesaPal environment
CONSUMER_KEY = "your_consumer_key_here"
CONSUMER_SECRET = "your_consumer_secret_here"

def test_pesapal_config():
    """Test PesaPal configuration endpoint"""
    print("=== Testing PesaPal Configuration ===")
    try:
        response = requests.get(f"{BASE_URL}/api/debug/pesapal-config")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_pesapal_auth():
    """Test PesaPal authentication directly"""
    print("\n=== Testing PesaPal Authentication ===")
    try:
        auth_url = f"{PESAPAL_BASE_URL}/Auth/RequestToken"
        auth_data = {
            'consumer_key': CONSUMER_KEY,
            'consumer_secret': CONSUMER_SECRET
        }
        
        print(f"Auth URL: {auth_url}")
        print(f"Consumer Key: {CONSUMER_KEY[:10]}..." if CONSUMER_KEY != "your_consumer_key_here" else "NOT CONFIGURED")
        print(f"Consumer Secret: {CONSUMER_SECRET[:10]}..." if CONSUMER_SECRET != "your_consumer_secret_here" else "NOT CONFIGURED")
        
        response = requests.post(auth_url, json=auth_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                token = data.get('token')
                if token:
                    print(f"✅ Authentication successful! Token: {token[:20]}...")
                    return token
                else:
                    print("❌ No token in response")
            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
        else:
            print("❌ Authentication failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def test_payment_request():
    """Test payment request"""
    print("\n=== Testing Payment Request ===")
    try:
        payment_data = {
            'resource_id': 1,  # Make sure this resource exists
            'email': 'test@example.com',
            'amount': 100.00,
            'name': 'Test User',
            'phone': '254700000000'
        }
        
        print(f"Payment Data: {json.dumps(payment_data, indent=2)}")
        
        response = requests.post(f"{BASE_URL}/api/pay", json=payment_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("PesaPal Integration Test Script")
    print("=" * 50)
    
    # Test 1: Configuration
    test_pesapal_config()
    
    # Test 2: Direct PesaPal authentication
    token = test_pesapal_auth()
    
    # Test 3: Payment request
    test_payment_request()
    
    print("\n" + "=" * 50)
    print("Test completed. Check the logs for detailed information.")

if __name__ == "__main__":
    main() 