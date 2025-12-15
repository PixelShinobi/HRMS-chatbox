"""
MongoDB Database Connection and Query Functions
"""
from pymongo import MongoClient
from pymongo.database import Database
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class HRDatabase:
    """HR Database Manager for MongoDB operations"""

    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.db_name = os.getenv("DB_NAME", "HRWIKI")
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None

    def connect(self):
        """Establish connection to local MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            # Test connection
            self.client.admin.command('ping')
            print(f"[+] Connected to MongoDB database: {self.db_name}")
            return True
        except Exception as e:
            print(f"[!] Failed to connect to MongoDB: {e}")
            print("[!] Please ensure MongoDB is running:")
            print("[!]   Windows: Check MongoDB service is started")
            print("[!]   Run: sc query MongoDB")
            return False

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("[+] MongoDB connection closed")

    # Employee queries
    def get_employee_by_id(self, employee_id: int) -> Optional[Dict[str, Any]]:
        """Get employee by ID"""
        try:
            collection = self.db["Employee and Visa sponsorship information"]
            employee = collection.find_one({"employeeid": employee_id})
            return employee
        except Exception as e:
            print(f"Error fetching employee {employee_id}: {e}")
            return None

    def search_employees(self, query: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Search employees with custom query"""
        try:
            collection = self.db["Employee and Visa sponsorship information"]
            employees = list(collection.find(query).limit(limit))
            return employees
        except Exception as e:
            print(f"Error searching employees: {e}")
            return []

    def get_all_employees(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all employees"""
        try:
            collection = self.db["Employee and Visa sponsorship information"]
            employees = list(collection.find().limit(limit))
            return employees
        except Exception as e:
            print(f"Error fetching all employees: {e}")
            return []

    def get_employees_with_visa_type(self, visa_type: str) -> List[Dict[str, Any]]:
        """Get employees with specific visa type"""
        try:
            collection = self.db["Employee and Visa sponsorship information"]
            # Search in summary field for visa type
            employees = list(collection.find({
                "summary": {"$regex": f"Visa type: {visa_type}", "$options": "i"}
            }))
            return employees
        except Exception as e:
            print(f"Error fetching employees with visa {visa_type}: {e}")
            return []

    def search_employees_by_role(self, role_name: str) -> List[Dict[str, Any]]:
        """Search employees by job role/position"""
        try:
            collection = self.db["Employee and Visa sponsorship information"]
            # Search in summary field for "Current Position: ... role_name ..."
            # Using regex to match the role name within the Current Position section
            employees = list(collection.find({
                "summary": {"$regex": f"Current Position:.*{role_name}", "$options": "i"}
            }))
            return employees
        except Exception as e:
            print(f"Error searching employees by role {role_name}: {e}")
            return []

    # Benefits and policy queries
    def get_possible_questions(self) -> List[Dict[str, Any]]:
        """Get predefined possible questions"""
        try:
            collection = self.db["Possible Questions Summary"]
            questions = list(collection.find())
            return questions
        except Exception as e:
            print(f"Error fetching possible questions: {e}")
            return []

    def get_employment_agreement(self) -> Optional[Dict[str, Any]]:
        """Get employment agreement template"""
        try:
            collection = self.db["EmploymentAgreement"]
            agreement = collection.find_one()
            return agreement
        except Exception as e:
            print(f"Error fetching employment agreement: {e}")
            return None

    def get_medical_plans(self) -> List[Dict[str, Any]]:
        """Get medical insurance plan information"""
        try:
            collection = self.db["Medical plan summary - Price Details 2025"]
            plans = list(collection.find())
            return plans
        except Exception as e:
            print(f"Error fetching medical plans: {e}")
            return []

    def get_dental_benefits(self) -> Optional[Dict[str, Any]]:
        """Get dental benefit information"""
        try:
            collection = self.db["Delta Dental Benefit Summary"]
            benefits = collection.find_one()
            return benefits
        except Exception as e:
            print(f"Error fetching dental benefits: {e}")
            return None

    def get_vision_benefits(self) -> Optional[Dict[str, Any]]:
        """Get vision benefit information"""
        try:
            collection = self.db["Delta Vision Benefit Summary"]
            benefits = collection.find_one()
            return benefits
        except Exception as e:
            print(f"Error fetching vision benefits: {e}")
            return None

# Global database instance
db = HRDatabase()
