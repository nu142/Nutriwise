import requests
import json
import sys
import os

class NutritionAPITester:
    def __init__(self, base_url="https://92e8a57e-565c-476f-a61a-306ae44bc398.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.sample_nutrition_data = {
            "food_name": "Greek Yogurt",
            "calories": 150,
            "total_fat": 8,
            "saturated_fat": 5,
            "trans_fat": 0,
            "cholesterol": 20,
            "sodium": 100,
            "total_carbs": 10,
            "dietary_fiber": 0,
            "total_sugars": 10,
            "added_sugars": 8,
            "protein": 15,
            "vitamin_d": 0,
            "calcium": 0,
            "iron": 0,
            "potassium": 0,
            "serving_size": "1 cup"
        }

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return success, response.json()
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        if success:
            print(f"Health status: {response.get('status')}")
            print(f"Models loaded: {response.get('models_loaded')}")
        return success

    def test_simplify_endpoint(self):
        """Test the nutrition simplification endpoint"""
        success, response = self.run_test(
            "Nutrition Simplification",
            "POST",
            "nutrition/simplify",
            200,
            data=self.sample_nutrition_data
        )
        if success:
            print(f"Simplified explanation: {response.get('simplified_explanation')}")
            print(f"Daily value percentages: {json.dumps(response.get('daily_value_percentages', {}), indent=2)}")
            print(f"Key insights: {json.dumps(response.get('key_insights', []), indent=2)}")
        return success

    def test_health_goal_endpoint(self):
        """Test the health goal suitability endpoint"""
        for goal in ["weight_loss", "muscle_gain", "heart_health", "diabetes_management"]:
            print(f"\nTesting health goal: {goal}")
            success, response = self.run_test(
                f"Health Goal - {goal}",
                "POST",
                "nutrition/health-goal",
                200,
                data={
                    "nutrition_data": self.sample_nutrition_data,
                    "health_goal": goal
                }
            )
            if success:
                print(f"Suitability verdict: {response.get('suitability_verdict')}")
                print(f"Suitability score: {response.get('suitability_score')}")
                print(f"Recommendation: {response.get('recommendation')}")
        return success

    def test_diet_compatibility_endpoint(self):
        """Test the diet compatibility endpoint"""
        for diet in ["keto", "vegan", "paleo", "mediterranean", "low_sodium"]:
            print(f"\nTesting diet compatibility: {diet}")
            success, response = self.run_test(
                f"Diet Compatibility - {diet}",
                "POST",
                "nutrition/diet-compatibility",
                200,
                data={
                    "nutrition_data": self.sample_nutrition_data,
                    "diet_type": diet
                }
            )
            if success:
                print(f"Compatibility explanation: {response.get('compatibility_explanation')}")
                print(f"Compatibility score: {response.get('compatibility_score')}")
                print(f"Is compatible: {response.get('is_compatible')}")
                print(f"Specific concerns: {json.dumps(response.get('specific_concerns', []), indent=2)}")
        return success

    def test_chat_endpoint(self):
        """Test the conversational query endpoint"""
        questions = [
            "Is this food healthy?",
            "How much protein does this have?",
            "Is this good for weight loss?",
            "What are the main nutrients in this food?"
        ]
        
        for question in questions:
            print(f"\nTesting chat with question: '{question}'")
            success, response = self.run_test(
                f"Chat - '{question}'",
                "POST",
                "nutrition/chat",
                200,
                data={
                    "nutrition_data": self.sample_nutrition_data,
                    "question": question,
                    "context": "This is a test context"
                }
            )
            if success:
                print(f"Question: {response.get('question')}")
                print(f"Answer: {response.get('answer')}")
                print(f"Follow-up suggestions: {json.dumps(response.get('follow_up_suggestions', []), indent=2)}")
        return success

    def test_warnings_endpoint(self):
        """Test the warnings and suggestions endpoint"""
        success, response = self.run_test(
            "Warnings and Suggestions",
            "POST",
            "nutrition/warnings",
            200,
            data=self.sample_nutrition_data
        )
        if success:
            print(f"AI analysis: {response.get('ai_analysis')}")
            print(f"Health warnings: {json.dumps(response.get('health_warnings', []), indent=2)}")
            print(f"Alternative suggestions: {json.dumps(response.get('alternative_suggestions', []), indent=2)}")
            print(f"Overall health score: {response.get('overall_health_score')}")
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("=" * 50)
        print("🧪 STARTING NUTRITION API TESTS")
        print("=" * 50)
        
        # Test all endpoints
        health_success = self.test_health_endpoint()
        simplify_success = self.test_simplify_endpoint()
        health_goal_success = self.test_health_goal_endpoint()
        diet_success = self.test_diet_compatibility_endpoint()
        chat_success = self.test_chat_endpoint()
        warnings_success = self.test_warnings_endpoint()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 SUMMARY: Tests passed: {self.tests_passed}/{self.tests_run}")
        print("=" * 50)
        
        # Test specific nutrition profiles
        print("\n🔍 TESTING DIFFERENT NUTRITION PROFILES")
        self.test_different_profiles()
        
        return self.tests_passed == self.tests_run

    def test_different_profiles(self):
        """Test different nutrition profiles"""
        profiles = [
            {
                "name": "High Sodium Food",
                "data": {**self.sample_nutrition_data, "food_name": "Canned Soup", "sodium": 1200}
            },
            {
                "name": "High Sugar Food",
                "data": {**self.sample_nutrition_data, "food_name": "Candy Bar", "added_sugars": 25, "total_sugars": 30}
            },
            {
                "name": "High Protein Food",
                "data": {**self.sample_nutrition_data, "food_name": "Protein Shake", "protein": 30, "calories": 200}
            }
        ]
        
        for profile in profiles:
            print(f"\nTesting profile: {profile['name']}")
            # Test warnings for this profile
            success, response = self.run_test(
                f"Warnings - {profile['name']}",
                "POST",
                "nutrition/warnings",
                200,
                data=profile['data']
            )
            if success:
                print(f"Health warnings: {json.dumps(response.get('health_warnings', []), indent=2)}")
                print(f"Overall health score: {response.get('overall_health_score')}")

def main():
    # Get API URL from environment or use default
    api_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://92e8a57e-565c-476f-a61a-306ae44bc398.preview.emergentagent.com')
    
    # Run tests
    tester = NutritionAPITester(api_url)
    success = tester.run_all_tests()
    
    # Return exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())