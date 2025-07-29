import requests
import json

# Test configuration
API_BASE = 'https://books-management-system-bcr5.onrender.com/api'

def test_simple_payment():
    """Test a simple payment request"""
    print("🧪 Testing Simple Payment")
    print("=" * 50)
    
    # Simple test data
    payment_data = {
        'resource_id': 1,
        'email': 'test@example.com',
        'amount': 100,
        'name': 'Test User',
        'phone': '+254700000000'
    }
    
    try:
        print(f"📡 Sending request to: {API_BASE}/pay")
        print(f"📋 Data: {json.dumps(payment_data, indent=2)}")
        
        response = requests.post(f'{API_BASE}/pay', json=payment_data, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Payment successful!")
            print(f"📋 Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Payment failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📋 Raw response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_backend_health():
    """Test if backend is healthy"""
    print("🏥 Testing Backend Health")
    print("=" * 50)
    
    try:
        # Test main endpoint
        response = requests.get(f'{API_BASE.replace("/api", "")}/', timeout=10)
        print(f"✅ Main endpoint: {response.status_code}")
        
        # Test resources endpoint
        response = requests.get(f'{API_BASE}/resources', timeout=10)
        print(f"✅ Resources endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📚 Found {len(data.get('books', []))} books")
            print(f"📚 Found {len(data.get('setbooks', []))} setbooks")
        
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    print("🚀 Simple Payment Test")
    print("=" * 60)
    
    # Test backend health first
    health_ok = test_backend_health()
    
    if not health_ok:
        print("\n❌ Backend not healthy. Cannot test payment.")
        return
    
    # Test payment
    payment_ok = test_simple_payment()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"Backend Health: {'✅' if health_ok else '❌'}")
    print(f"Payment: {'✅' if payment_ok else '❌'}")
    
    if payment_ok:
        print("\n🎉 Payment system is working!")
    else:
        print("\n⚠️  Payment system has issues.")
        print("\n🔧 Possible solutions:")
        print("1. Check PesaPal credentials in Render environment variables")
        print("2. Verify PesaPal service is accessible")
        print("3. Check backend logs for specific error messages")

if __name__ == "__main__":
    main() 