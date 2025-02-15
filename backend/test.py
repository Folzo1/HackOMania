import requests
import json
import uuid
from pathlib import Path
import time

BASE_URL = "http://localhost:8000"
TEST_SESSION_ID = str(uuid.uuid4())
IMG_DIR = Path("img")

def test_server_connection():
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Server connection test - Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("Failed to connect to server. Is it running?")
        return False

def detailed_request_test(endpoint, method='POST', **kwargs):
    print(f"\nTesting {method} {endpoint}")
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", **kwargs) if method.upper() == 'POST' else requests.get(f"{BASE_URL}{endpoint}", **kwargs)
        print(f"Status Code: {response.status_code}\nResponse Content: {response.text[:200]}...")
        return response
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def test_scan_endpoint():
    image_files = list(IMG_DIR.glob("*.jpg"))
    if not image_files:
        print("No images found in img directory.")
        return None
    files = {"images": (img.name, open(img, "rb"), "image/jpeg") for img in image_files}
    data = {"session_id": TEST_SESSION_ID}
    response = detailed_request_test("/scan", files=files, data=data)
    for img in image_files:
        files["images"][1].close()
    return response

def test_generate_recipe_endpoint():
    data = {"session_id": TEST_SESSION_ID}
    return detailed_request_test("/generate_recipe", json=data)

def test_publish_endpoint():
    data = {
        "recipe_name": "Test Recipe",
        "ingredients": ["Ingredient 1", "Ingredient 2"],
        "instructions": "Step 1: Do something. Step 2: Do something else.",
        "image_url": "http://example.com/test.jpg"
    }
    return detailed_request_test("/publish", json=data)

if __name__ == "__main__":
    print(f"Starting endpoint tests...\nBase URL: {BASE_URL}\nTest Session ID: {TEST_SESSION_ID}")
    if not test_server_connection():
        exit(1)
    time.sleep(1)
    print("\n=== Testing /scan endpoint ===")
    test_scan_endpoint()
    print("\n=== Testing /generate_recipe endpoint ===")
    test_generate_recipe_endpoint()
    print("\n=== Testing /publish endpoint ===")
    test_publish_endpoint()
