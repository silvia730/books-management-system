#!/usr/bin/env python3
"""
Test script for the PesaPal IPN system
This script helps verify that the IPN endpoint is working correctly
"""

import requests
import json
from datetime import datetime

def test_ipn_endpoint(base_url="http://localhost:5000"):
    """Test the IPN endpoint with sample data"""
    
    # Sample IPN data (this would come from PesaPal)
    ipn_data = {
        'transaction_tracking_id': 'TEST_TRANS_123',
        'merchant_reference': 'TEST_ORDER_456',
        'status': 'COMPLETED'
    }
    
    # Test IPN endpoint
    ipn_url = f"{base_url}/api/pesapal/ipn"
    
    print(f"Testing IPN endpoint: {ipn_url}")
    print(f"IPN Data: {json.dumps(ipn_data, indent=2)}")
    
    try:
        # Send GET request with query parameters (as PesaPal would)
        response = requests.get(ipn_url, params=ipn_data)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ IPN endpoint is working!")
        else:
            print("❌ IPN endpoint returned an error")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to IPN endpoint: {e}")

def test_payment_endpoints(base_url="http://localhost:5000"):
    """Test payment-related endpoints"""
    
    print("\n" + "="*50)
    print("Testing Payment Endpoints")
    print("="*50)
    
    # Test getting all payments
    try:
        response = requests.get(f"{base_url}/api/payments")
        print(f"GET /api/payments - Status: {response.status_code}")
        if response.status_code == 200:
            payments = response.json()
            print(f"Found {len(payments.get('payments', []))} payments")
    except Exception as e:
        print(f"Error testing /api/payments: {e}")
    
    # Test getting specific payment
    try:
        response = requests.get(f"{base_url}/api/payment/TEST_ORDER_456")
        print(f"GET /api/payment/TEST_ORDER_456 - Status: {response.status_code}")
    except Exception as e:
        print(f"Error testing /api/payment: {e}")

def test_health_check(base_url="http://localhost:5000"):
    """Test if the server is running"""
    
    print("\n" + "="*50)
    print("Health Check")
    print("="*50)
    
    try:
        response = requests.get(f"{base_url}/api/resources")
        print(f"Server Status: {'✅ Running' if response.status_code == 200 else '❌ Error'}")
        print(f"Response Code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Start with: python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("PesaPal IPN System Test")
    print("="*50)
    
    # Test if server is running
    test_health_check()
    
    # Test payment endpoints
    test_payment_endpoints()
    
    # Test IPN endpoint
    test_ipn_endpoint()
    
    print("\n" + "="*50)
    print("Test completed!")
    print("="*50)
    print("\nTo test with real PesaPal data:")
    print("1. Deploy your app to a public URL")
    print("2. Configure the IPN URL in PesaPal dashboard")
    print("3. Make a test payment")
    print("4. Check the logs for IPN activity") 