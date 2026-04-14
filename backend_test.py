#!/usr/bin/env python3
"""
Divine Waifus Backend Regression Testing
Tests all backend endpoints after refactoring from monolithic game_systems.py to modular /routes/ structure
"""
import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "http://localhost:8001/api"

# Test credentials
TEST_EMAIL = "test@test.com"
TEST_PASSWORD = "password123"

class APITester:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.results = []
        
    def log_result(self, endpoint, method, status_code, success, error=None, response_data=None):
        """Log test result"""
        result = {
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'success': success,
            'error': error,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {method} {endpoint} - {status_code}")
        if error:
            print(f"    Error: {error}")
        if response_data and not success:
            print(f"    Response: {response_data}")
    
    def login(self):
        """Login to get authentication token"""
        print(f"\n🔐 Logging in with {TEST_EMAIL}...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                if self.token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}'
                    })
                    print(f"✅ Login successful! Token: {self.token[:20]}...")
                    return True
                else:
                    print("❌ Login failed: No token in response")
                    return False
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def test_endpoint(self, endpoint, method="GET", data=None, auth_required=True, expected_status=200):
        """Test a single endpoint"""
        url = f"{BACKEND_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            elif method == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = response.status_code == expected_status
            response_data = None
            error = None
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            if not success:
                error = f"Expected {expected_status}, got {response.status_code}"
                if response_data:
                    error += f" - {response_data}"
            
            self.log_result(endpoint, method, response.status_code, success, error, response_data if not success else None)
            return success, response_data
            
        except Exception as e:
            self.log_result(endpoint, method, 0, False, str(e))
            return False, None
    
    def run_regression_tests(self):
        """Run all regression tests as specified in review request"""
        print("🚀 Starting Divine Waifus Backend Regression Test")
        print("🔄 Testing after refactoring from monolithic game_systems.py to modular /routes/")
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Login first
        if not self.login():
            print("❌ Cannot proceed without authentication")
            return False
        
        print("\n📋 Testing All Endpoints from Review Request...")
        
        # All 23 endpoints from the review request
        test_cases = [
            # 1. Auth (already done in login)
            
            # 2. Equipment
            ("/equipment/templates", "GET", None, True, 200),
            
            # 3. Story
            ("/story/chapters", "GET", None, True, 200),
            
            # 4. Tower
            ("/tower/status", "GET", None, True, 200),
            
            # 5. PvP
            ("/pvp/status", "GET", None, True, 200),
            
            # 6. Guild
            ("/guild/info", "GET", None, True, 200),
            
            # 7. Factions
            ("/factions", "GET", None, True, 200),
            
            # 8. Events
            ("/events/daily", "GET", None, True, 200),
            
            # 9. Cosmetics
            ("/cosmetics", "GET", None, True, 200),
            
            # 10. Territory
            ("/territory/map", "GET", None, True, 200),
            
            # 11. Plaza Chat
            ("/plaza/chat", "GET", None, True, 200),
            
            # 12. Raids
            ("/raids", "GET", None, True, 200),
            
            # 13. Exclusive Items
            ("/exclusive-items", "GET", None, True, 200),
            
            # 14. Rankings Arena
            ("/rankings/arena", "GET", None, True, 200),
            
            # 15. Rankings Power
            ("/rankings/power", "GET", None, True, 200),
            
            # 16. Shop
            ("/shop", "GET", None, True, 200),
            
            # 17. Mail
            ("/mail", "GET", None, True, 200),
            
            # 18. Battle Pass
            ("/battlepass", "GET", None, True, 200),
            
            # 19. Servers (no auth needed)
            ("/servers", "GET", None, False, 200),
            
            # 20. VIP
            ("/vip", "GET", None, True, 200),
            
            # 21. Friends
            ("/friends", "GET", None, True, 200),
            
            # 22. Bot Status
            ("/admin/bots/status", "GET", None, True, 200),
            
            # 23. Health (no auth needed)
            ("/health", "GET", None, False, 200),
        ]
        
        print(f"Testing {len(test_cases)} endpoints...")
        print("-" * 60)
        
        passed = 0
        failed = 0
        
        for endpoint, method, data, auth_required, expected_status in test_cases:
            success, response_data = self.test_endpoint(endpoint, method, data, auth_required, expected_status)
            if success:
                passed += 1
                # Verify JSON response
                if response_data and isinstance(response_data, dict):
                    print(f"    ✅ Valid JSON response received")
                elif response_data and isinstance(response_data, list):
                    print(f"    ✅ Valid JSON array response received")
                else:
                    print(f"    ⚠️  Response format: {type(response_data)}")
            else:
                failed += 1
        
        print("\n" + "=" * 60)
        print("📊 REGRESSION TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed > 0:
            print("\n🔍 FAILED ENDPOINTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   ❌ {result['method']} {result['endpoint']} - {result['error']}")
        else:
            print("\n🎉 All regression tests passed! Backend refactoring successful.")
        
        return failed == 0
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  • {result['method']} {result['endpoint']} - {result['status_code']}")
                    if result['error']:
                        print(f"    {result['error']}")
        
        print("\n" + "=" * 60)
        return failed_tests == 0

def main():
    """Main test function"""
    tester = APITester()
    
    try:
        success = tester.run_regression_tests()
        all_passed = tester.print_summary()
        
        if all_passed:
            print("🎉 All regression tests passed! Backend refactoring successful.")
            sys.exit(0)
        else:
            print("💥 Some regression tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()