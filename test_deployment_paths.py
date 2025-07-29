#!/usr/bin/env python3
"""
Test script to verify file paths for deployment
"""

import os
import sys

def test_file_paths():
    """Test if all required files exist for deployment"""
    
    # Get the current directory (should be the project root)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Current directory: {current_dir}")
    
    # Test admin files
    admin_files = [
        'admin/admin.html',
        'admin/admin.css',
        'admin/admin-script.js',
        'admin/assets/somafy logo.jpg'
    ]
    
    print("\n🔍 Testing Admin Files:")
    admin_missing = []
    for file_path in admin_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            admin_missing.append(file_path)
    
    # Test user files
    user_files = [
        'user/index.html',
        'user/style.css',
        'user/script.js',
        'user/resources.html',
        'user/resources.js',
        'user/assets/somafy logo.jpg',
        'user/assets/exam paper2.jpg',
        'user/assets/WhatsApp Image 2025-07-21 at 17.39.48_efa085dc.jpg'
    ]
    
    print("\n🔍 Testing User Files:")
    user_missing = []
    for file_path in user_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            user_missing.append(file_path)
    
    # Test backend files
    backend_files = [
        'backend/app.py',
        'backend/models.py',
        'backend/config.py'
    ]
    
    print("\n🔍 Testing Backend Files:")
    backend_missing = []
    for file_path in backend_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            backend_missing.append(file_path)
    
    # Summary
    print("\n📋 Summary:")
    if not admin_missing and not user_missing and not backend_missing:
        print("✅ All files are present! Deployment should work.")
        return True
    else:
        print("❌ Some files are missing:")
        if admin_missing:
            print(f"  - Admin files missing: {len(admin_missing)}")
        if user_missing:
            print(f"  - User files missing: {len(user_missing)}")
        if backend_missing:
            print(f"  - Backend files missing: {len(backend_missing)}")
        return False

def test_flask_routes():
    """Test if Flask routes can find the files"""
    print("\n🧪 Testing Flask Route Paths:")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Test admin dashboard path
    admin_path = os.path.join(current_dir, 'admin', 'admin.html')
    print(f"Admin dashboard path: {admin_path}")
    print(f"  - Exists: {'✅' if os.path.exists(admin_path) else '❌'}")
    
    # Test user dashboard path
    user_path = os.path.join(current_dir, 'user', 'index.html')
    print(f"User dashboard path: {user_path}")
    print(f"  - Exists: {'✅' if os.path.exists(user_path) else '❌'}")

def main():
    """Main function"""
    print("🚀 Deployment Path Test")
    print("=" * 50)
    
    success = test_file_paths()
    test_flask_routes()
    
    if success:
        print("\n🎉 All tests passed! Your deployment should work correctly.")
        print("\n📝 Deployment URLs:")
        print("  - Admin Dashboard: https://your-domain.com/admin")
        print("  - User Dashboard: https://your-domain.com/user")
        print("  - API Base: https://your-domain.com/api")
    else:
        print("\n⚠️  Some issues found. Please fix them before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main() 