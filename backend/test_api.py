import json
import urllib.request

def test_register():
    url = "http://127.0.0.1:5000/register"
    data = {
        "username": "testuser_from_script",
        "password": "password123"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    json_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            print("--- Register Test ---")
            print(f"Status: {response.status}")
            print("Response Body:")
            print(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print("--- Register Test ---")
        print(f"Error: {e.code}")
        print(e.read().decode('utf-8'))

def test_login():
    url = "http://127.0.0.1:5000/login"
    data = {
        "username": "testuser_from_script",
        "password": "password123"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    json_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            print("\n--- Login Test ---")
            print(f"Status: {response.status}")
            print("Response Body:")
            print(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print("\n--- Login Test ---")
        print(f"Error: {e.code}")
        print(e.read().decode('utf-8'))

if __name__ == "__main__":
    # test_register() # Comment out after first successful registration
    test_login()