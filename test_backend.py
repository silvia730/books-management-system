import requests
import json
import time

# Test configuration
API_BASE = 'https://books-management-system-bcr5.onrender.com/api'

def test_backend_connectivity():
    """Test if the backend is accessible"""
    try:
        response = requests.get(f'{API_BASE.replace("/api", "")}/')
        print(f"✅ Backend connectivity: {response.status_code}")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Backend connectivity failed: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    try:
        # Use a unique username to avoid conflicts
        import random
        unique_id = random.randint(1000, 9999)
        test_user = {
            'username': f'testuser{unique_id}',
            'email': f'testuser{unique_id}@example.com',
            'password': 'testpassword123'
        }
        
        response = requests.post(f'{API_BASE}/register', json=test_user)
        print(f"✅ User registration: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.json().get('success'):
            return test_user  # Return the user data for login test
        return None
    except Exception as e:
        print(f"❌ User registration failed: {e}")
        return None

def test_user_login(user_data):
    """Test user login"""
    try:
        if not user_data:
            print("❌ No user data provided for login test")
            return None
            
        login_data = {
            'username': user_data['username'],
            'password': user_data['password']
        }
        
        response = requests.post(f'{API_BASE}/login', json=login_data)
        print(f"✅ User login: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"❌ User login failed: {e}")
        return None

def test_resources_endpoint():
    """Test resources endpoint"""
    try:
        response = requests.get(f'{API_BASE}/resources')
        print(f"✅ Resources endpoint: {response.status_code}")
        data = response.json()
        print(f"Books: {len(data.get('books', []))}")
        print(f"Papers: {len(data.get('papers', []))}")
        print(f"Setbooks: {len(data.get('setbooks', []))}")
        
        # Show sample data
        if data.get('books'):
            print(f"Sample book: {data['books'][0]}")
        if data.get('setbooks'):
            print(f"Sample setbook: {data['setbooks'][0]}")
            
        return data
    except Exception as e:
        print(f"❌ Resources endpoint failed: {e}")
        return None

def test_payment_endpoint():
    """Test payment endpoint"""
    try:
        payment_data = {
            'resource_id': 1,
            'email': 'testuser123@example.com',
            'amount': 100,
            'name': 'Test User',
            'phone': '+254700000000'
        }
        
        response = requests.post(f'{API_BASE}/pay', json=payment_data)
        print(f"✅ Payment endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"❌ Payment endpoint failed: {e}")
        return None

def test_existing_user_login():
    """Test login with existing user (admin)"""
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = requests.post(f'{API_BASE}/login', json=login_data)
        print(f"✅ Admin login: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"❌ Admin login failed: {e}")
        return None

def main():
    print("🧪 Testing Backend Functionality")
    print("=" * 50)
    
    # Test 1: Backend connectivity
    if not test_backend_connectivity():
        print("❌ Backend is not accessible. Please check your deployment.")
        return
    
    # Test 2: User registration
    user_data = test_user_registration()
    
    # Wait a moment for database to update
    time.sleep(2)
    
    # Test 3: User login with newly registered user
    if user_data:
        login_result = test_user_login(user_data)
    else:
        login_result = None
    
    # Test 4: Admin login (should work)
    admin_login_result = test_existing_user_login()
    
    # Test 5: Resources endpoint
    resources_result = test_resources_endpoint()
    
    # Test 6: Payment endpoint
    payment_result = test_payment_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"Backend Connectivity: {'✅' if test_backend_connectivity() else '❌'}")
    print(f"User Registration: {'✅' if user_data else '❌'}")
    print(f"User Login: {'✅' if login_result and login_result.get('success') else '❌'}")
    print(f"Admin Login: {'✅' if admin_login_result and admin_login_result.get('success') else '❌'}")
    print(f"Resources Endpoint: {'✅' if resources_result else '❌'}")
    print(f"Payment Endpoint: {'✅' if payment_result else '❌'}")

if __name__ == "__main__":
    main() 