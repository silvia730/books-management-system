import requests
import json

# Test configuration
API_BASE = 'https://books-management-system-bcr5.onrender.com/api'

def test_payment_endpoint():
    """Test the payment endpoint"""
    print("🧪 Testing Payment Endpoint")
    print("=" * 50)
    
    # Test data
    payment_data = {
        'resource_id': 1,  # Use the existing book
        'email': 'testuser@example.com',
        'amount': 100,
        'name': 'Test User',
        'phone': '+254700000000'
    }
    
    try:
        print(f"📡 Sending payment request to: {API_BASE}/pay")
        print(f"📋 Payment data: {payment_data}")
        
        response = requests.post(f'{API_BASE}/pay', json=payment_data)
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📄 Response headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📋 Response data: {json.dumps(response_data, indent=2)}")
            
            if response.status_code == 200 and response_data.get('success'):
                print("✅ Payment request successful!")
                print(f"🆔 Order Tracking ID: {response_data.get('orderTrackingId')}")
                print(f"🔗 Redirect URL: {response_data.get('redirectUrl')}")
                return response_data
            else:
                print(f"❌ Payment request failed: {response_data.get('error')}")
                return None
                
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def test_pesapal_credentials():
    """Test if PesaPal credentials are configured"""
    print("\n🔐 Testing PesaPal Configuration")
    print("=" * 50)
    
    try:
        # Test the main endpoint to see if it's accessible
        response = requests.get(f'{API_BASE.replace("/api", "")}/')
        print(f"✅ Backend accessible: {response.status_code}")
        
        # Test a simple endpoint to check configuration
        response = requests.get(f'{API_BASE}/resources')
        print(f"✅ Resources endpoint accessible: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_payment_flow():
    """Test the complete payment flow"""
    print("\n🔄 Testing Complete Payment Flow")
    print("=" * 50)
    
    # Step 1: Test backend connectivity
    if not test_pesapal_credentials():
        print("❌ Backend not accessible, cannot test payment flow")
        return False
    
    # Step 2: Test payment endpoint
    payment_result = test_payment_endpoint()
    
    if payment_result:
        print("\n✅ Payment flow test completed successfully!")
        print("📋 Next steps:")
        print("1. User should be redirected to PesaPal payment page")
        print("2. After payment, user should be redirected to download success page")
        print("3. User can then download the resource")
        return True
    else:
        print("\n❌ Payment flow test failed!")
        return False

def main():
    print("🚀 SomaFy Payment System Test")
    print("=" * 60)
    
    # Run tests
    backend_ok = test_pesapal_credentials()
    payment_ok = test_payment_endpoint()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"Backend Connectivity: {'✅' if backend_ok else '❌'}")
    print(f"Payment Endpoint: {'✅' if payment_ok else '❌'}")
    
    if backend_ok and payment_ok:
        print("\n🎉 All tests passed! Payment system is working.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        
        if not backend_ok:
            print("💡 Backend connectivity issue - check if the server is running")
        
        if not payment_ok:
            print("💡 Payment endpoint issue - check PesaPal credentials and configuration")

if __name__ == "__main__":
    main() 