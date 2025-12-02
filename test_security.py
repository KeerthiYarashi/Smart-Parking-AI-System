import urllib.request
import urllib.error
import json
import os

BASE_URL = "http://localhost:8000"

# Simple .env parser to avoid extra dependencies for this test script
def get_env_key():
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.strip().startswith('SECRET_KEY='):
                    return line.strip().split('=', 1)[1]
    except FileNotFoundError:
        pass
    return "SECRET123" # Fallback

VALID_KEY = get_env_key()
INVALID_KEY = "WRONG_KEY"

def send_request(endpoint, payload, headers=None):
    if headers is None: headers = {}
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode('utf-8')
    
    headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except urllib.error.URLError as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)

def print_result(test_name, status, body, expected_status):
    is_pass = status == expected_status
    icon = "✅ PASS" if is_pass else "❌ FAIL"
    
    print(f"{'-'*60}")
    print(f"{icon}: {test_name}")
    print(f"   Expected Status: {expected_status}")
    print(f"   Actual Status:   {status}")
    
    # Pretty print JSON response
    try:
        if body:
            json_obj = json.loads(body)
            formatted_body = json.dumps(json_obj, indent=2)
            # Indent for display
            formatted_body = "\n".join(["      " + line for line in formatted_body.split("\n")])
            print(f"   Server Response:\n{formatted_body}")
        else:
            print("   Server Response: <empty>")
    except:
        print(f"   Server Response: {body}")
    print("\n")

def run_tests():
    print("\n🛡️  STARTING SECURITY CHECKS (Standard Lib)\n")
    print("NOTE: We EXPECT errors (403/422) for invalid inputs.")
    print("      A 'PASS' means the server correctly blocked the attack.\n")

    # 1. TEST AUTHENTICATION (No Key)
    status, body = send_request("/api/entry", {"type": "NORMAL", "duration": 1})
    if status is None:
        print(f"❌ Connection Failed: {body}")
        print("   Ensure server is running: python main.py")
        return
    print_result("Auth Check: Missing Header", status, body, 403)

    # 2. TEST AUTHENTICATION (Wrong Key)
    status, body = send_request("/api/entry", {"type": "NORMAL", "duration": 1}, {"X-API-KEY": INVALID_KEY})
    print_result("Auth Check: Wrong Key", status, body, 403)

    # 3. TEST INPUT VALIDATION (Negative Duration)
    status, body = send_request("/api/entry", {"type": "NORMAL", "duration": -5}, {"X-API-KEY": VALID_KEY})
    print_result("Validation: Negative Duration", status, body, 422)

    # 4. TEST SANITIZATION (Script Injection)
    # Pydantic will reject the <script> tag because it's not a valid Vehicle Type
    status, body = send_request("/api/entry", {"type": "<script>alert('hack')</script>", "duration": 1}, {"X-API-KEY": VALID_KEY})
    print_result("Sanitization: Script Injection", status, body, 422)

    # 5. TEST VALID REQUEST
    status, body = send_request("/api/entry", {"type": "NORMAL", "duration": 1}, {"X-API-KEY": VALID_KEY})
    print_result("Valid Request: Normal Entry", status, body, 200)

if __name__ == "__main__":
    run_tests()
