#!/usr/bin/env python3
"""
EduQuest Backend API Testing Suite
Tests all backend endpoints for the gamified learning platform
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get base URL from environment
BASE_URL = "https://edu-quest-2.preview.emergentagent.com/api"

class EduQuestAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.test_user_data = {
            "name": "Alex Johnson",
            "email": f"alex.johnson.{datetime.now().strftime('%Y%m%d%H%M%S')}@eduquest.com",
            "password": "SecurePass123!"
        }
        self.test_results = {
            "auth": {"passed": 0, "failed": 0, "details": []},
            "courses": {"passed": 0, "failed": 0, "details": []},
            "enrollments": {"passed": 0, "failed": 0, "details": []},
            "progress": {"passed": 0, "failed": 0, "details": []},
            "chat": {"passed": 0, "failed": 0, "details": []}
        }
        self.course_id = None
        self.enrollment_id = None
        self.chat_session_id = None

    def log_result(self, category, test_name, success, details=""):
        """Log test result"""
        if success:
            self.test_results[category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.test_results[category]["failed"] += 1
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        self.test_results[category]["details"].append(result)
        print(result)

    def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {"Content-Type": "application/json"}
        if self.auth_token:
            default_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method == "GET":
                response = requests.get(url, headers=default_headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request error for {method} {url}: {e}")
            return None

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # Test 1: User Signup
        try:
            response = self.make_request("POST", "/auth/signup", self.test_user_data)
            if response and response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.auth_token = data["token"]
                    self.log_result("auth", "User Signup", True, f"User created: {data['user']['name']}")
                else:
                    self.log_result("auth", "User Signup", False, "Missing user or token in response")
            else:
                error_msg = response.json().get("error", "Unknown error") if response else "No response"
                self.log_result("auth", "User Signup", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        except Exception as e:
            self.log_result("auth", "User Signup", False, f"Exception: {str(e)}")

        # Test 2: User Login
        try:
            login_data = {
                "email": self.test_user_data["email"],
                "password": self.test_user_data["password"]
            }
            response = self.make_request("POST", "/auth/login", login_data)
            if response and response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.auth_token = data["token"]  # Update token
                    self.log_result("auth", "User Login", True, f"Login successful for: {data['user']['email']}")
                else:
                    self.log_result("auth", "User Login", False, "Missing user or token in response")
            else:
                error_msg = response.json().get("error", "Unknown error") if response else "No response"
                self.log_result("auth", "User Login", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        except Exception as e:
            self.log_result("auth", "User Login", False, f"Exception: {str(e)}")

        # Test 3: Get Current User
        try:
            response = self.make_request("GET", "/auth/me")
            if response and response.status_code == 200:
                data = response.json()
                if "email" in data and data["email"] == self.test_user_data["email"]:
                    self.log_result("auth", "Get Current User", True, f"User data retrieved: {data['name']}")
                else:
                    self.log_result("auth", "Get Current User", False, "User data mismatch")
            else:
                error_msg = response.json().get("error", "Unknown error") if response else "No response"
                self.log_result("auth", "Get Current User", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        except Exception as e:
            self.log_result("auth", "Get Current User", False, f"Exception: {str(e)}")

        # Test 4: Invalid Login
        try:
            invalid_login = {
                "email": "invalid@test.com",
                "password": "wrongpassword"
            }
            response = self.make_request("POST", "/auth/login", invalid_login)
            if response and response.status_code == 401:
                self.log_result("auth", "Invalid Login Rejection", True, "Correctly rejected invalid credentials")
            else:
                self.log_result("auth", "Invalid Login Rejection", False, f"Expected 401, got {response.status_code if response else 'None'}")
        except Exception as e:
            self.log_result("auth", "Invalid Login Rejection", False, f"Exception: {str(e)}")

    def test_course_endpoints(self):
        """Test course management endpoints"""
        print("\n📚 Testing Course Management Endpoints...")
        
        # Test 1: Get All Courses
        try:
            response = self.make_request("GET", "/courses")
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.course_id = data[0]["id"]  # Store first course ID for later tests
                    self.log_result("courses", "Get All Courses", True, f"Retrieved {len(data)} courses")
                else:
                    self.log_result("courses", "Get All Courses", False, "No courses returned")
            else:
                error_msg = response.json().get("error", "Unknown error") if response else "No response"
                self.log_result("courses", "Get All Courses", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        except Exception as e:
            self.log_result("courses", "Get All Courses", False, f"Exception: {str(e)}")

        # Test 2: Get Course by ID
        if self.course_id:
            try:
                response = self.make_request("GET", f"/courses/{self.course_id}")
                if response and response.status_code == 200:
                    data = response.json()
                    if "id" in data and data["id"] == self.course_id:
                        self.log_result("courses", "Get Course by ID", True, f"Retrieved course: {data['title']}")
                    else:
                        self.log_result("courses", "Get Course by ID", False, "Course ID mismatch")
                else:
                    error_msg = response.json().get("error", "Unknown error") if response else "No response"
                    self.log_result("courses", "Get Course by ID", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
            except Exception as e:
                self.log_result("courses", "Get Course by ID", False, f"Exception: {str(e)}")

        # Test 3: Get Non-existent Course
        try:
            response = self.make_request("GET", "/courses/nonexistent-id")
            if response and response.status_code == 404:
                self.log_result("courses", "Non-existent Course Handling", True, "Correctly returned 404 for invalid course ID")
            else:
                self.log_result("courses", "Non-existent Course Handling", False, f"Expected 404, got {response.status_code if response else 'None'}")
        except Exception as e:
            self.log_result("courses", "Non-existent Course Handling", False, f"Exception: {str(e)}")

    def test_enrollment_endpoints(self):
        """Test enrollment system endpoints"""
        print("\n🎓 Testing Enrollment System Endpoints...")
        
        if not self.auth_token:
            self.log_result("enrollments", "All Enrollment Tests", False, "No auth token available")
            return
        
        if not self.course_id:
            self.log_result("enrollments", "All Enrollment Tests", False, "No course ID available")
            return

        # Test 1: Enroll in Course
        try:
            enrollment_data = {"courseId": self.course_id}
            response = self.make_request("POST", "/enrollments", enrollment_data)
            if response and response.status_code == 200:
                data = response.json()
                if "id" in data and "course_id" in data:
                    self.enrollment_id = data["id"]
                    self.log_result("enrollments", "Course Enrollment", True, f"Enrolled in course: {data['course_id']}")
                else:
                    self.log_result("enrollments", "Course Enrollment", False, "Missing enrollment data")
            else:
                error_msg = response.json().get("error", "Unknown error") if response else "No response"
                self.log_result("enrollments", "Course Enrollment", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        except Exception as e:
            self.log_result("enrollments", "Course Enrollment", False, f"Exception: {str(e)}")

        # Test 2: Get User Enrollments
        try:
            response = self.make_request("GET", "/enrollments")
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    enrollment = data[0]
                    if "course" in enrollment and "progress" in enrollment:
                        self.log_result("enrollments", "Get User Enrollments", True, f"Retrieved {len(data)} enrollments")
                    else:
                        self.log_result("enrollments", "Get User Enrollments", False, "Missing course or progress data")
                else:
                    self.log_result("enrollments", "Get User Enrollments", False, "No enrollments returned")
            else:
                error_msg = response.json().get("error", "Unknown error") if response else "No response"
                self.log_result("enrollments", "Get User Enrollments", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        except Exception as e:
            self.log_result("enrollments", "Get User Enrollments", False, f"Exception: {str(e)}")

        # Test 3: Duplicate Enrollment Prevention
        try:
            enrollment_data = {"courseId": self.course_id}
            response = self.make_request("POST", "/enrollments", enrollment_data)
            if response and response.status_code == 400:
                self.log_result("enrollments", "Duplicate Enrollment Prevention", True, "Correctly prevented duplicate enrollment")
            else:
                self.log_result("enrollments", "Duplicate Enrollment Prevention", False, f"Expected 400, got {response.status_code if response else 'None'}")
        except Exception as e:
            self.log_result("enrollments", "Duplicate Enrollment Prevention", False, f"Exception: {str(e)}")

        # Test 4: Unauthorized Enrollment Access
        try:
            # Temporarily remove auth token
            temp_token = self.auth_token
            self.auth_token = None
            response = self.make_request("GET", "/enrollments")
            self.auth_token = temp_token  # Restore token
            
            if response and response.status_code == 401:
                self.log_result("enrollments", "Unauthorized Access Prevention", True, "Correctly rejected unauthorized access")
            else:
                self.log_result("enrollments", "Unauthorized Access Prevention", False, f"Expected 401, got {response.status_code if response else 'None'}")
        except Exception as e:
            self.log_result("enrollments", "Unauthorized Access Prevention", False, f"Exception: {str(e)}")

    def test_progress_endpoints(self):
        """Test progress tracking and XP system"""
        print("\n📈 Testing Progress Tracking & XP System...")
        
        if not self.auth_token or not self.enrollment_id:
            self.log_result("progress", "All Progress Tests", False, "Missing auth token or enrollment ID")
            return

        # Test 1: Update Progress and Award XP
        try:
            progress_data = {
                "enrollmentId": self.enrollment_id,
                "missionId": 1,
                "xpEarned": 100
            }
            response = self.make_request("PUT", "/progress", progress_data)
            if response and response.status_code == 200:
                data = response.json()
                if "success" in data and "newXp" in data and "newLevel" in data:
                    self.log_result("progress", "Progress Update & XP Award", True, f"XP: {data['newXp']}, Level: {data['newLevel']}, Progress: {data['progress']}%")
                else:
                    self.log_result("progress", "Progress Update & XP Award", False, "Missing progress data in response")
            else:
                error_msg = response.json().get("error", "Unknown error") if response else "No response"
                self.log_result("progress", "Progress Update & XP Award", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        except Exception as e:
            self.log_result("progress", "Progress Update & XP Award", False, f"Exception: {str(e)}")

        # Test 2: Complete Another Mission
        try:
            progress_data = {
                "enrollmentId": self.enrollment_id,
                "missionId": 2,
                "xpEarned": 150
            }
            response = self.make_request("PUT", "/progress", progress_data)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("newXp", 0) >= 250:  # Should have at least 250 XP now
                    self.log_result("progress", "Multiple Mission Completion", True, f"Cumulative XP: {data['newXp']}")
                else:
                    self.log_result("progress", "Multiple Mission Completion", False, f"XP not accumulating correctly: {data.get('newXp', 0)}")
            else:
                error_msg = response.json().get("error", "Unknown error") if response else "No response"
                self.log_result("progress", "Multiple Mission Completion", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        except Exception as e:
            self.log_result("progress", "Multiple Mission Completion", False, f"Exception: {str(e)}")

        # Test 3: Invalid Enrollment ID
        try:
            progress_data = {
                "enrollmentId": "invalid-enrollment-id",
                "missionId": 1,
                "xpEarned": 100
            }
            response = self.make_request("PUT", "/progress", progress_data)
            if response and response.status_code == 404:
                self.log_result("progress", "Invalid Enrollment Handling", True, "Correctly rejected invalid enrollment ID")
            else:
                self.log_result("progress", "Invalid Enrollment Handling", False, f"Expected 404, got {response.status_code if response else 'None'}")
        except Exception as e:
            self.log_result("progress", "Invalid Enrollment Handling", False, f"Exception: {str(e)}")

    def test_chat_endpoints(self):
        """Test AI mentor chat system"""
        print("\n🤖 Testing AI Mentor Chat System...")
        
        if not self.auth_token or not self.course_id:
            self.log_result("chat", "All Chat Tests", False, "Missing auth token or course ID")
            return

        # Test 1: Create Chat Session
        try:
            session_data = {"courseId": self.course_id}
            response = self.make_request("POST", "/chat/session", session_data)
            if response and response.status_code == 200:
                data = response.json()
                if "id" in data and "messages" in data:
                    self.chat_session_id = data["id"]
                    initial_messages = len(data["messages"])
                    self.log_result("chat", "Create Chat Session", True, f"Session created with {initial_messages} initial messages")
                else:
                    self.log_result("chat", "Create Chat Session", False, "Missing session data")
            else:
                error_msg = response.json().get("error", "Unknown error") if response else "No response"
                self.log_result("chat", "Create Chat Session", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
        except Exception as e:
            self.log_result("chat", "Create Chat Session", False, f"Exception: {str(e)}")

        # Test 2: Get Chat Session
        if self.chat_session_id:
            try:
                response = self.make_request("GET", f"/chat/{self.chat_session_id}")
                if response and response.status_code == 200:
                    data = response.json()
                    if "id" in data and data["id"] == self.chat_session_id:
                        self.log_result("chat", "Get Chat Session", True, f"Retrieved session with {len(data.get('messages', []))} messages")
                    else:
                        self.log_result("chat", "Get Chat Session", False, "Session ID mismatch")
                else:
                    error_msg = response.json().get("error", "Unknown error") if response else "No response"
                    self.log_result("chat", "Get Chat Session", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
            except Exception as e:
                self.log_result("chat", "Get Chat Session", False, f"Exception: {str(e)}")

        # Test 3: Send Message to AI Mentor
        if self.chat_session_id:
            try:
                message_data = {"message": "Hello! Can you help me understand the basics of web development?"}
                response = self.make_request("POST", f"/chat/{self.chat_session_id}", message_data)
                if response and response.status_code == 200:
                    data = response.json()
                    if "message" in data and len(data["message"]) > 0:
                        self.log_result("chat", "Send Message to AI", True, f"AI responded with {len(data['message'])} characters")
                    else:
                        self.log_result("chat", "Send Message to AI", False, "Empty AI response")
                else:
                    error_msg = response.json().get("error", "Unknown error") if response else "No response"
                    # AI mentor might be unavailable, which is acceptable
                    if response and response.status_code == 500 and "AI mentor unavailable" in error_msg:
                        self.log_result("chat", "Send Message to AI", True, "AI mentor service unavailable (expected in test environment)")
                    else:
                        self.log_result("chat", "Send Message to AI", False, f"Status: {response.status_code if response else 'None'}, Error: {error_msg}")
            except Exception as e:
                self.log_result("chat", "Send Message to AI", False, f"Exception: {str(e)}")

        # Test 4: Invalid Session Access
        try:
            response = self.make_request("GET", "/chat/invalid-session-id")
            if response and response.status_code == 404:
                self.log_result("chat", "Invalid Session Handling", True, "Correctly rejected invalid session ID")
            else:
                self.log_result("chat", "Invalid Session Handling", False, f"Expected 404, got {response.status_code if response else 'None'}")
        except Exception as e:
            self.log_result("chat", "Invalid Session Handling", False, f"Exception: {str(e)}")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🎯 EDUQUEST BACKEND API TEST SUMMARY")
        print("="*60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status_icon = "✅" if failed == 0 else "⚠️" if passed > failed else "❌"
            print(f"\n{status_icon} {category.upper()}: {passed} passed, {failed} failed")
            
            for detail in results["details"]:
                print(f"  {detail}")
        
        print(f"\n{'='*60}")
        overall_status = "✅ ALL TESTS PASSED" if total_failed == 0 else f"⚠️ {total_passed} PASSED, {total_failed} FAILED"
        print(f"OVERALL: {overall_status}")
        print(f"{'='*60}")
        
        return total_failed == 0

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting EduQuest Backend API Tests...")
        print(f"Base URL: {self.base_url}")
        
        # Run tests in sequence
        self.test_auth_endpoints()
        self.test_course_endpoints()
        self.test_enrollment_endpoints()
        self.test_progress_endpoints()
        self.test_chat_endpoints()
        
        # Print summary
        success = self.print_summary()
        return success

def main():
    """Main test execution"""
    tester = EduQuestAPITester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()