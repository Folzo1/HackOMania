import requests
import json
import uuid
from pathlib import Path
import time

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_IMAGE_PATH = "img/coke1.jpg"
TEST_SESSION_ID = str(uuid.uuid4())

def test_server_connection():
    """Basic test to check if server is responding"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Server connection test - Status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        return True
    except requests.exceptions.ConnectionError:
        print("Failed to connect to server. Is it running?")
        return False

def detailed_request_test(endpoint, method='POST', **kwargs):
    """Make a request with detailed logging"""
    print(f"\nTesting {method} {endpoint}")
    print(f"Request parameters: {kwargs}")
    
    try:
        if method.upper() == 'POST':
            response = requests.post(f"{BASE_URL}{endpoint}", **kwargs)
        else:
            response = requests.get(f"{BASE_URL}{endpoint}", **kwargs)
            
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: {response.text[:200]}...")  # First 200 chars
        
        return response
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def test_scan_endpoint():
    """Test the /scan endpoint with detailed logging"""
    if not Path(TEST_IMAGE_PATH).exists():
        print(f"Creating dummy test image at {TEST_IMAGE_PATH}")
        # Create a small dummy image file for testing
        with open(TEST_IMAGE_PATH, 'wb') as f:
            f.write(b'dummy image content')
    
    files = {
        'image': ('test_barcode.jpg', open(TEST_IMAGE_PATH, 'rb'), 'image/jpeg')
    }
    data = {
        'session_id': TEST_SESSION_ID
    }
    
    return detailed_request_test('/scan', files=files, data=data)

def test_generate_recipe_endpoint():
    """Test the /generate_recipe endpoint with detailed logging"""
    data = {
        "session_id": TEST_SESSION_ID
    }
    
    return detailed_request_test('/generate_recipe', json=data)

if __name__ == "__main__":
    print("Starting endpoint tests with detailed logging...")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Session ID: {TEST_SESSION_ID}")
    
    # First check if server is running
    if not test_server_connection():
        print("Cannot proceed with tests - server not responding")
        exit(1)
    
    # Wait a moment for server to be fully ready
    time.sleep(1)
    
    # Run tests with detailed output
    print("\n=== Testing /scan endpoint ===")
    scan_response = test_scan_endpoint()
    
    print("\n=== Testing /generate_recipe endpoint ===")
    recipe_response = test_generate_recipe_endpoint()
    
    # Clean up test image
    if Path(TEST_IMAGE_PATH).exists():
        Path(TEST_IMAGE_PATH).unlink()