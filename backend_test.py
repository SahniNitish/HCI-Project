import requests
import sys
import json
from datetime import datetime, timedelta
import time

class ExpenseTrackerAPITester:
    def __init__(self, base_url="https://budget-insight-20.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "status": "PASSED" if success else "FAILED",
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text[:200]}"
                
                self.log_test(name, False, error_msg)
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration"""
        test_email = f"test_user_{int(time.time())}@example.com"
        test_data = {
            "email": test_email,
            "password": "TestPass123!",
            "name": "Test User"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=test_data
        )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['id']
            return True
        return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        # First register a user
        test_email = f"login_test_{int(time.time())}@example.com"
        register_data = {
            "email": test_email,
            "password": "TestPass123!",
            "name": "Login Test User"
        }
        
        # Register user
        success, _ = self.run_test(
            "User Registration for Login Test",
            "POST",
            "auth/register",
            200,
            data=register_data
        )
        
        if not success:
            return False
        
        # Now test login
        login_data = {
            "email": test_email,
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        return success and 'token' in response

    def test_get_user_profile(self):
        """Test getting user profile"""
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_add_expense_with_ai(self):
        """Test adding expense with AI categorization"""
        expense_data = {
            "amount": 25.50,
            "description": "Lunch at McDonald's",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "category": None  # Let AI categorize
        }
        
        success, response = self.run_test(
            "Add Expense with AI Categorization",
            "POST",
            "expenses",
            200,
            data=expense_data
        )
        
        if success and response.get('ai_categorized'):
            print(f"   AI categorized as: {response.get('category')}")
            return response.get('id')  # Return expense ID for later tests
        return None

    def test_add_expense_manual(self):
        """Test adding expense with manual category"""
        expense_data = {
            "amount": 15.75,
            "description": "Bus fare",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "category": "Transportation"
        }
        
        success, response = self.run_test(
            "Add Expense with Manual Category",
            "POST",
            "expenses",
            200,
            data=expense_data
        )
        
        if success:
            return response.get('id')  # Return expense ID for later tests
        return None

    def test_get_expenses(self):
        """Test getting all expenses"""
        success, response = self.run_test(
            "Get All Expenses",
            "GET",
            "expenses",
            200
        )
        
        if success:
            print(f"   Found {len(response)} expenses")
        return success

    def test_delete_expense(self, expense_id):
        """Test deleting an expense"""
        if not expense_id:
            self.log_test("Delete Expense", False, "No expense ID provided")
            return False
            
        success, _ = self.run_test(
            "Delete Expense",
            "DELETE",
            f"expenses/{expense_id}",
            200
        )
        return success

    def test_set_budget(self):
        """Test setting a budget"""
        current_date = datetime.now()
        budget_data = {
            "category": "Food",
            "limit": 500.00,
            "month": current_date.month,
            "year": current_date.year
        }
        
        success, response = self.run_test(
            "Set Budget",
            "POST",
            "budgets",
            200,
            data=budget_data
        )
        return success

    def test_get_budgets(self):
        """Test getting all budgets"""
        success, response = self.run_test(
            "Get All Budgets",
            "GET",
            "budgets",
            200
        )
        
        if success:
            print(f"   Found {len(response)} budgets")
        return success

    def test_dashboard_stats(self):
        """Test getting dashboard statistics"""
        success, response = self.run_test(
            "Get Dashboard Stats",
            "GET",
            "dashboard/stats",
            200
        )
        
        if success:
            print(f"   Total expenses: ${response.get('total_expenses', 0):.2f}")
            print(f"   Expense count: {response.get('expense_count', 0)}")
            print(f"   Top category: {response.get('top_category', 'None')}")
        return success

    def test_ai_financial_advice(self):
        """Test AI financial advice generation"""
        print(f"\n🔍 Testing AI Financial Advice...")
        print("   This may take a few seconds as AI generates advice...")
        
        success, response = self.run_test(
            "Get AI Financial Advice",
            "GET",
            "ai/financial-advice",
            200
        )
        
        if success and response.get('advice'):
            advice_preview = response['advice'][:100] + "..." if len(response['advice']) > 100 else response['advice']
            print(f"   Generated advice: {advice_preview}")
        return success

    def test_get_ai_insights(self):
        """Test getting AI insights history"""
        success, response = self.run_test(
            "Get AI Insights History",
            "GET",
            "ai/insights",
            200
        )
        
        if success:
            print(f"   Found {len(response)} AI insights")
        return success

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Expense Tracker API Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 60)

        # Authentication Tests
        print("\n📋 AUTHENTICATION TESTS")
        if not self.test_user_registration():
            print("❌ Registration failed - stopping tests")
            return False
        
        self.test_user_login()
        self.test_get_user_profile()

        # Expense Management Tests
        print("\n💰 EXPENSE MANAGEMENT TESTS")
        expense_id_ai = self.test_add_expense_with_ai()
        expense_id_manual = self.test_add_expense_manual()
        self.test_get_expenses()
        
        # Test deletion with one of the created expenses
        if expense_id_manual:
            self.test_delete_expense(expense_id_manual)

        # Budget Management Tests
        print("\n📊 BUDGET MANAGEMENT TESTS")
        self.test_set_budget()
        self.test_get_budgets()

        # Analytics Tests
        print("\n📈 ANALYTICS TESTS")
        self.test_dashboard_stats()

        # AI Features Tests
        print("\n🤖 AI FEATURES TESTS")
        self.test_ai_financial_advice()
        # Wait a moment for the insight to be saved
        time.sleep(2)
        self.test_get_ai_insights()

        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 FINAL RESULTS")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = ExpenseTrackerAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": tester.tests_run,
        "passed_tests": tester.tests_passed,
        "success_rate": (tester.tests_passed/tester.tests_run*100) if tester.tests_run > 0 else 0,
        "all_passed": success,
        "detailed_results": tester.test_results
    }
    
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())