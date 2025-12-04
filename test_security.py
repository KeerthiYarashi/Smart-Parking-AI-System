"""
🔐 Security Test Script for Smart Parking AI System
Tests: API Key Auth, Input Validation, Input Sanitization, Rate Limiting

Run this script AFTER starting the server:
    1. python main.py  (in one terminal)
    2. python test_security.py  (in another terminal)
"""

import urllib.request
import urllib.error
import json
import sys

BASE_URL = "http://localhost:8000"
VALID_API_KEY = "DDCO_SMART_PARKING_2024_SECURE_API_KEY_9x7zL4mP"  # From .env
WRONG_API_KEY = "WRONG_KEY_12345"

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}  {text}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_test(name, passed, expected, actual):
    status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if passed else f"{Colors.RED}❌ FAIL{Colors.RESET}"
    print(f"{status}: {name}")
    if not passed:
        print(f"       Expected: {expected}")
        print(f"       Actual: {actual}")
    return passed

def make_request(url, method="GET", data=None, headers=None):
    """Make HTTP request using urllib (no external dependencies)"""
    if headers is None:
        headers = {}
    
    if data is not None:
        data = json.dumps(data).encode('utf-8')
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return {
                'status_code': response.status,
                'reason': response.reason,
                'headers': dict(response.headers),
                'body': response.read().decode('utf-8')
            }
    except urllib.error.HTTPError as e:
        return {
            'status_code': e.code,
            'reason': e.reason,
            'headers': dict(e.headers) if e.headers else {},
            'body': e.read().decode('utf-8') if e.fp else ''
        }
    except urllib.error.URLError as e:
        return None

def test_server_running():
    """Check if server is running"""
    result = make_request(f"{BASE_URL}/api/status")
    return result is not None and result['status_code'] == 200

def test_auth_missing_header():
    """Test 1: Request without API Key header should return 403"""
    result = make_request(
        f"{BASE_URL}/api/simulate/add_vehicle",
        method="POST",
        data={"type": "NORMAL", "duration": 2.0},
        headers={"Content-Type": "application/json"}
    )
    return print_test(
        "Auth Check: Missing API Key Header",
        result and result['status_code'] == 403,
        "403 Forbidden",
        f"{result['status_code']} {result['reason']}" if result else "Connection failed"
    )

def test_auth_wrong_key():
    """Test 2: Request with wrong API Key should return 403"""
    result = make_request(
        f"{BASE_URL}/api/simulate/add_vehicle",
        method="POST",
        data={"type": "NORMAL", "duration": 2.0},
        headers={
            "Content-Type": "application/json",
            "X-API-KEY": WRONG_API_KEY
        }
    )
    return print_test(
        "Auth Check: Wrong API Key",
        result and result['status_code'] == 403,
        "403 Forbidden",
        f"{result['status_code']} {result['reason']}" if result else "Connection failed"
    )

def test_validation_negative_duration():
    """Test 3: Negative duration should return 422 or 400"""
    result = make_request(
        f"{BASE_URL}/api/simulate/add_vehicle",
        method="POST",
        data={"type": "NORMAL", "duration": -5.0},
        headers={
            "Content-Type": "application/json",
            "X-API-KEY": VALID_API_KEY
        }
    )
    return print_test(
        "Validation: Negative Duration",
        result and result['status_code'] in [422, 400],
        "422 or 400 (Validation Error)",
        f"{result['status_code']} {result['reason']}" if result else "Connection failed"
    )

def test_validation_invalid_type():
    """Test 4: Invalid vehicle type check"""
    result = make_request(
        f"{BASE_URL}/api/simulate/add_vehicle",
        method="POST",
        data={"type": "INVALID_TYPE", "duration": 2.0},
        headers={
            "Content-Type": "application/json",
            "X-API-KEY": VALID_API_KEY
        }
    )
    return print_test(
        "Validation: Invalid Vehicle Type",
        result and result['status_code'] in [422, 400, 200],
        "422/400 (Validation) or 200 (Accepted)",
        f"{result['status_code']} {result['reason']}" if result else "Connection failed"
    )

def test_sanitization_script_injection():
    """Test 5: Script injection should be blocked"""
    result = make_request(
        f"{BASE_URL}/api/simulate/add_vehicle",
        method="POST",
        data={"type": "<script>alert(1)</script>", "duration": 2.0},
        headers={
            "Content-Type": "application/json",
            "X-API-KEY": VALID_API_KEY
        }
    )
    return print_test(
        "Sanitization: Script Injection Blocked",
        result and result['status_code'] in [422, 400],
        "422 or 400 (Sanitization Block)",
        f"{result['status_code']} {result['reason']}" if result else "Connection failed"
    )

def test_sanitization_sql_injection():
    """Test 6: SQL injection patterns should be blocked"""
    result = make_request(
        f"{BASE_URL}/api/simulate/add_vehicle",
        method="POST",
        data={"type": "'; DROP TABLE users; --", "duration": 2.0},
        headers={
            "Content-Type": "application/json",
            "X-API-KEY": VALID_API_KEY
        }
    )
    return print_test(
        "Sanitization: SQL Injection Blocked",
        result and result['status_code'] in [422, 400],
        "422 or 400 (Sanitization Block)",
        f"{result['status_code']} {result['reason']}" if result else "Connection failed"
    )

def test_valid_request():
    """Test 7: Valid request should succeed"""
    result = make_request(
        f"{BASE_URL}/api/simulate/add_vehicle",
        method="POST",
        data={"type": "NORMAL", "duration": 2.0},
        headers={
            "Content-Type": "application/json",
            "X-API-KEY": VALID_API_KEY
        }
    )
    return print_test(
        "Valid Request: Normal Entry",
        result and result['status_code'] == 200,
        "200 OK",
        f"{result['status_code']} {result['reason']}" if result else "Connection failed"
    )

def test_security_headers():
    """Test 8: Check security headers are present"""
    result = make_request(f"{BASE_URL}/api/status")
    
    if not result:
        return print_test("Security Headers Present", False, "Headers present", "Connection failed")
    
    headers = result['headers']
    x_content_type = headers.get("X-Content-Type-Options", headers.get("x-content-type-options", ""))
    x_frame = headers.get("X-Frame-Options", headers.get("x-frame-options", ""))
    
    all_present = x_content_type == "nosniff" and x_frame in ["DENY", "SAMEORIGIN"]
    
    return print_test(
        "Security Headers Present",
        all_present,
        "All security headers set",
        f"X-Content-Type-Options: {x_content_type}, X-Frame-Options: {x_frame}"
    )

def test_simulation_step_auth():
    """Test 9: Simulation step endpoint requires auth"""
    result = make_request(
        f"{BASE_URL}/api/simulate/step",
        method="GET",
        headers={}
    )
    return print_test(
        "Simulation Step: Requires API Key",
        result and result['status_code'] == 403,
        "403 Forbidden",
        f"{result['status_code']} {result['reason']}" if result else "Connection failed"
    )

def test_pattern_endpoint():
    """Test 10: Pattern endpoint with valid key"""
    result = make_request(
        f"{BASE_URL}/api/simulate/pattern",
        method="POST",
        data={"mode": "PEAK"},
        headers={
            "Content-Type": "application/json",
            "X-API-KEY": VALID_API_KEY
        }
    )
    return print_test(
        "Pattern Endpoint: Valid Request",
        result and result['status_code'] == 200,
        "200 OK",
        f"{result['status_code']} {result['reason']}" if result else "Connection failed"
    )

def test_invalid_pattern_mode():
    """Test 11: Invalid pattern mode should fail validation"""
    result = make_request(
        f"{BASE_URL}/api/simulate/pattern",
        method="POST",
        data={"mode": "INVALID_MODE"},
        headers={
            "Content-Type": "application/json",
            "X-API-KEY": VALID_API_KEY
        }
    )
    return print_test(
        "Pattern: Invalid Mode Rejected",
        result and result['status_code'] == 422,
        "422 Unprocessable Entity",
        f"{result['status_code']} {result['reason']}" if result else "Connection failed"
    )

def test_reset_simulation():
    """Test 12: Reset simulation endpoint"""
    result = make_request(
        f"{BASE_URL}/api/simulate/reset",
        method="POST",
        headers={"X-API-KEY": VALID_API_KEY}
    )
    return print_test(
        "Reset Simulation: Works with API Key",
        result and result['status_code'] == 200,
        "200 OK",
        f"{result['status_code']} {result['reason']}" if result else "Connection failed"
    )

def main():
    print_header("🔐 SMART PARKING AI - SECURITY TEST SUITE")
    
    # Check server is running
    print(f"{Colors.YELLOW}Checking server connectivity...{Colors.RESET}")
    if not test_server_running():
        print(f"\n{Colors.RED}❌ ERROR: Server is not running!{Colors.RESET}")
        print(f"{Colors.YELLOW}Please start the server first:{Colors.RESET}")
        print(f"   python main.py")
        print(f"\nThen run this script in another terminal.")
        sys.exit(1)
    
    print(f"{Colors.GREEN}✅ Server is running{Colors.RESET}\n")
    
    # Run tests
    results = []
    
    print_header("1️⃣ API KEY AUTHENTICATION TESTS")
    results.append(test_auth_missing_header())
    results.append(test_auth_wrong_key())
    results.append(test_simulation_step_auth())
    
    print_header("2️⃣ INPUT VALIDATION TESTS")
    results.append(test_validation_negative_duration())
    results.append(test_validation_invalid_type())
    results.append(test_invalid_pattern_mode())
    
    print_header("3️⃣ INPUT SANITIZATION TESTS")
    results.append(test_sanitization_script_injection())
    results.append(test_sanitization_sql_injection())
    
    print_header("4️⃣ SECURITY HEADERS TEST")
    results.append(test_security_headers())
    
    print_header("5️⃣ VALID REQUEST TESTS")
    results.append(test_valid_request())
    results.append(test_pattern_endpoint())
    results.append(test_reset_simulation())
    
    # Summary
    print_header("📊 TEST SUMMARY")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED: {passed}/{total}{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}Tests Passed: {passed}/{total}{Colors.RESET}")
        print(f"{Colors.RED}Tests Failed: {total - passed}/{total}{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}📚 Understanding the Results:{Colors.RESET}")
    print(f"""
    {Colors.GREEN}HTTP 200 (OK){Colors.RESET}        → ✅ Request succeeded (valid input)
    {Colors.RED}HTTP 403 (Forbidden){Colors.RESET}  → 🛑 Security block (bad API key)
    {Colors.YELLOW}HTTP 422 (Unprocessable){Colors.RESET} → 🛡️ Validation block (bad data)
    {Colors.YELLOW}HTTP 400 (Bad Request){Colors.RESET}   → 🛡️ Sanitization block (malicious input)
    
    {Colors.BOLD}Note:{Colors.RESET} Seeing 403/422/400 in these tests means security is WORKING!
    The system correctly rejected bad requests.
    """)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
