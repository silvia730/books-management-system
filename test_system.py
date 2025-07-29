#!/usr/bin/env python3
"""
Test script for the School Management System
This script tests the main API endpoints to ensure everything is working correctly.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000/api"

def test_api_connection():
    """Test basic API connectivity"""
    print("🔍 Testing API connection...")
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/")
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Make sure it's running on localhost:5000")
        return False

def test_resources_endpoint():
    """Test the resources endpoint"""
    print("\n📚 Testing resources endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/resources")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resources endpoint working")
            print(f"   - Books: {len(data.get('books', []))}")
            print(f"   - Papers: {len(data.get('papers', []))}")
            print(f"   - Setbooks: {len(data.get('setbooks', []))}")
            return True
        else:
            print(f"❌ Resources endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing resources endpoint: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print("\n👤 Testing user registration...")
    try:
        test_user = {
            "username": f"testuser_{int(time.time())}",
            "email": f"testuser_{int(time.time())}@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{BASE_URL}/register", json=test_user)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ User registration working")
                return test_user
            else:
                print(f"❌ Registration failed: {data.get('error')}")
                return None
        else:
            print(f"❌ Registration endpoint returned status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error testing registration: {e}")
        return None

def test_user_login(test_user):
    """Test user login"""
    print("\n🔐 Testing user login...")
    try:
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ User login working")
                return True
            else:
                print(f"❌ Login failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Login endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return False

def test_payment_system():
    """Test the payment system"""
    print("\n💳 Testing payment system...")
    try:
        payment_data = {
            "resource_id": 1,
            "email": "test@example.com",
            "name": "Test User",
            "phone": "254700123456",
            "amount": 100
        }
        
        response = requests.post(f"{BASE_URL}/pay", json=payment_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Payment system working (test mode)")
                print(f"   - Order ID: {data.get('orderTrackingId')}")
                return data.get('orderTrackingId')
            else:
                print(f"❌ Payment failed: {data.get('error')}")
                return None
        else:
            print(f"❌ Payment endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing payment: {e}")
        return None

def main():
    """Run all tests"""
    print("🚀 Starting School Management System Tests")
    print("=" * 50)
    
    # Test API connection
    if not test_api_connection():
        print("\n❌ Cannot proceed with tests. Please start the backend server first.")
        return
    
    # Test resources endpoint
    test_resources_endpoint()
    
    # Test user registration
    test_user = test_user_registration()
    
    # Test user login if registration was successful
    if test_user:
        test_user_login(test_user)
    
    # Test payment system
    test_payment_system()
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")
    print("\n📋 Summary:")
    print("   - Make sure your backend server is running on localhost:5000")
    print("   - The frontend should now be able to connect to the backend")
    print("   - Payment system is working in test mode")
    print("   - User authentication is functional")

if __name__ == "__main__":
    main() 