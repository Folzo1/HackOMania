import requests
import json
import uuid
from pathlib import Path
import time

# Test configuration
BASE_URL = "http://localhost:8000"
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
    # Create multiple dummy test images
    test_images = [
        ("img/coke1.jpg", b"dummy image 1 content"),
        ("img/coke2.jpg", b"dummy image 2 content"),
        ("img/crysanthemum.jpg", b"dummy image 3 content")
    ]
    
    # Prepare files for upload
    files = []
    for path, _ in test_images:
        img_path = Path(path)
        files.append(('images', (img_path.name, open(img_path, 'rb'), 'image/jpeg')))
    
    data = {'session_id': TEST_SESSION_ID}
    
    # Make the request
    response = detailed_request_test('/scan', files=files, data=data)
    
    # Close open file handles
    for file_tuple in files:
        file_tuple[1][1].close()
    
    return response

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