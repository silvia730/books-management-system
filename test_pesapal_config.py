import requests
import json

# Test configuration
API_BASE = 'https://books-management-system-bcr5.onrender.com/api'

def test_pesapal_config():
    """Test PesaPal configuration"""
    print("🔐 Testing PesaPal Configuration")
    print("=" * 50)
    
    # Test data for a simple payment
    payment_data = {
        'resource_id': 1,
        'email': 'test@example.com',
        'amount': 100,
        'name': 'Test User',
        'phone': '+254700000000'
    }
    
    try:
        print("📡 Testing payment endpoint...")
        response = requests.post(f'{API_BASE}/pay', json=payment_data)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Payment endpoint working!")
            print(f"📋 Response: {json.dumps(data, indent=2)}")
            return True
        elif response.status_code == 503:
            data = response.json()
            error_msg = data.get('error', 'Unknown error')
            print(f"⚠️  Payment service issue: {error_msg}")
            
            if "configuration error" in error_msg.lower():
                print("💡 Issue: PesaPal credentials not properly configured")
                print("🔧 Solution: Check environment variables on Render:")
                print("   - PESAPAL_CONSUMER_KEY")
                print("   - PESAPAL_CONSUMER_SECRET")
                print("   - PESAPAL_BASE_URL")
            else:
                print("💡 Issue: PesaPal service temporarily unavailable")
            
            return False
        else:
            data = response.json()
            print(f"❌ Payment endpoint error: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_backend_health():
    """Test backend health"""
    print("🏥 Testing Backend Health")
    print("=" * 50)
    
    try:
        response = requests.get(f'{API_BASE.replace("/api", "")}/')
        print(f"✅ Backend accessible: {response.status_code}")
        
        response = requests.get(f'{API_BASE}/resources')
        print(f"✅ Resources endpoint: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def main():
    print("🚀 PesaPal Configuration Test")
    print("=" * 60)
    
    # Test backend health first
    backend_ok = test_backend_health()
    
    if not backend_ok:
        print("\n❌ Backend not accessible. Cannot test PesaPal configuration.")
        return
    
    # Test PesaPal configuration
    pesapal_ok = test_pesapal_config()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"Backend Health: {'✅' if backend_ok else '❌'}")
    print(f"PesaPal Config: {'✅' if pesapal_ok else '❌'}")
    
    if backend_ok and pesapal_ok:
        print("\n🎉 PesaPal is properly configured and working!")
    else:
        print("\n⚠️  PesaPal configuration issues detected.")
        print("\n🔧 To fix PesaPal issues:")
        print("1. Go to your Render dashboard")
        print("2. Navigate to your backend service")
        print("3. Go to Environment variables")
        print("4. Ensure these variables are set:")
        print("   - PESAPAL_CONSUMER_KEY")
        print("   - PESAPAL_CONSUMER_SECRET")
        print("   - PESAPAL_BASE_URL")
        print("   - PESAPAL_NOTIFICATION_ID")
        print("5. Redeploy your service")

if __name__ == "__main__":
    main() 