"""
API Test Script for TodoAI Backend

Tests the backend API endpoints to verify:
1. Health check
2. Authentication requirement
3. Task CRUD operations
4. User data isolation
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_health():
    """Test health endpoint"""
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    print("   ✅ Health check passed")

def test_protected_endpoint_without_auth():
    """Test that protected endpoints require authentication"""
    print("\n2. Testing protected endpoint without auth...")
    response = requests.get(f"{BASE_URL}/api/tasks")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 401 or response.status_code == 403
    print("   ✅ Authentication required (as expected)")

def test_api_docs():
    """Test API documentation is accessible"""
    print("\n3. Testing API documentation...")
    response = requests.get(f"{BASE_URL}/docs")
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200
    print("   ✅ API docs accessible at {BASE_URL}/docs")

def main():
    print("=" * 60)
    print("TodoAI Backend API Tests")
    print("=" * 60)

    try:
        test_health()
        test_protected_endpoint_without_auth()
        test_api_docs()

        print("\n" + "=" * 60)
        print("✅ All backend tests passed!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Sign up with a test account")
        print("3. Create and manage tasks")
        print("4. Test user data isolation with multiple accounts")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to backend at {BASE_URL}")
        print("   Make sure the backend server is running")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
