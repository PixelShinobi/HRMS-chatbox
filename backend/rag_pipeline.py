"""
RAG (Retrieval-Augmented Generation) Pipeline for HR Chatbot
Enhanced context retrieval with role-based access control
"""
from typing import List, Dict, Any, Optional, Tuple
import re
from datetime import datetime, timedelta
from database import db

class HRQueryProcessor:
    """Process and classify HR queries for better context retrieval"""

    # Query type classifications
    QUERY_TYPES = {
        "EMPLOYEE_LOOKUP": ["employee id", "employee number", "find employee", "who is employee"],
        "VISA_STATUS": ["visa status", "immigration", "h-1b", "h1b", "green card", "opt", "cpt", "visa type", "visa expiration"],
        "BENEFITS": ["health insurance", "medical plan", "dental", "vision", "401k", "benefits"],
        "POLICY": ["sick days", "vacation", "pto", "paid time off", "holiday", "leave policy"],
        "EMPLOYMENT_INFO": ["join date", "hired", "started", "position", "title", "salary", "pay", "contract type"],
        "TERMINATION": ["terminated", "left", "resignation", "end date"],
        "STATISTICS": ["how many", "count", "total", "number of", "list all", "which employees", "who has", "show me all", "show all"],
        "JOB_ROLE": ["manager", "developer", "analyst", "consultant", "executive", "position", "role", "working as", "title"],
    }

    # Sensitive keywords that require HR Lead access
    SENSITIVE_KEYWORDS = [
        "salary", "pay", "compensation", "wage", "hourly rate",
        "terminated", "termination", "fired", "resignation", "end date",
        "visa expiration", "visa expires", "visa expiring", "when does visa"
    ]

    @staticmethod
    def classify_query(query: str) -> List[str]:
        """Classify query into one or more types"""
        query_lower = query.lower()
        classifications = []

        for query_type, keywords in HRQueryProcessor.QUERY_TYPES.items():
            if any(keyword in query_lower for keyword in keywords):
                classifications.append(query_type)

        return classifications if classifications else ["GENERAL"]

    @staticmethod
    def is_sensitive_query(query: str, query_types: List[str]) -> bool:
        """
        Determine if query requests sensitive/restricted information
        Returns True for queries that should be restricted to HR leads
        """
        query_lower = query.lower()

        # Check for sensitive keywords
        has_sensitive_keyword = any(kw in query_lower for kw in HRQueryProcessor.SENSITIVE_KEYWORDS)

        # Employee-specific queries with sensitive query types
        has_employee_id = bool(HRQueryProcessor.extract_employee_ids(query))
        is_sensitive_type = any(qt in ["EMPLOYMENT_INFO", "TERMINATION"] for qt in query_types)

        # Salary query with employee ID is always sensitive
        if has_employee_id and ("salary" in query_lower or "pay" in query_lower or "compensation" in query_lower):
            return True

        # Individual visa expiration query with employee ID is sensitive
        if has_employee_id and ("visa expir" in query_lower or "when does" in query_lower and "visa" in query_lower):
            return True

        # Termination queries are always sensitive
        if "TERMINATION" in query_types:
            return True

        return has_sensitive_keyword and has_employee_id

    @staticmethod
    def sanitize_employee_summary(employee_summary: str) -> str:
        """
        Remove sensitive information from employee summary for junior HR
        Removes: salary, termination info, specific visa expiration dates
        """
        lines = employee_summary.split('. ')
        sanitized_parts = []

        for line in lines:
            line_lower = line.lower()

            # Check for salary information
            if any(kw in line_lower for kw in ['salary', 'annual salary', 'hourly rate', '$']):
                # Skip salary lines entirely or replace
                if 'salary' in line_lower or '$' in line:
                    sanitized_parts.append("[Salary information restricted - HR Lead access required]")
                    continue

            # Check for termination information
            if any(kw in line_lower for kw in ['terminated', 'termination date', 'end date']):
                sanitized_parts.append("[Employment status restricted - HR Lead access required]")
                continue

            # Check for specific visa expiration dates (but allow visa type)
            if 'visa' in line_lower and any(kw in line_lower for kw in ['expir', 'end date', 'valid until']):
                # Keep visa type but hide expiration
                sanitized_parts.append("[Visa expiration details restricted - HR Lead access required]")
                continue

            # Keep other information
            sanitized_parts.append(line)

        return '. '.join(sanitized_parts)

    @staticmethod
    def extract_employee_ids(query: str) -> List[int]:
        """Extract employee IDs from query (4-digit numbers between 1000-9999)"""
        # Look for 4-digit numbers that could be employee IDs
        matches = re.findall(r'\b(1[4-5]\d{2})\b', query)  # IDs seem to be in 1400-1599 range
        return [int(match) for match in matches]

    @staticmethod
    def extract_timeframe(query: str) -> Optional[str]:
        """Extract timeframe from query (e.g., '6 months', '1 year')"""
        # Look for patterns like "in 6 months", "within 1 year", "next 3 months"
        patterns = [
            r'(?:in|within|next)\s+(\d+)\s+(month|year)s?',
            r'(\d+)\s+(month|year)s?',
        ]

        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                number = match.group(1)
                unit = match.group(2)
                return f"{number} {unit}s"

        return None

    @staticmethod
    def extract_visa_type(query: str) -> Optional[str]:
        """Extract visa type from query"""
        visa_types = ["H-1B", "Green Card", "OPT", "CPT", "TN Visa", "Citizen", "OPT-Extension", "H-1B Extension"]

        query_lower = query.lower()
        for visa_type in visa_types:
            if visa_type.lower() in query_lower:
                return visa_type

        return None

    @staticmethod
    def extract_job_role(query: str) -> Optional[str]:
        """Extract job role from query"""
        # Common roles to look for
        roles = [
            "Technical Project Manager", "Project Manager",
            "Software Developer", "Developer", "Software Engineer",
            "Sales Executive", "Sales",
            "Test Analyst", "QA", "Quality Assurance", "Tester",
            "Consultant", "Support Executive"
        ]

        query_lower = query.lower()
        for role in roles:
            if role.lower() in query_lower:
                return role

        return None


class RAGPipeline:
    """Enhanced RAG Pipeline for HR Chatbot with Role-Based Access Control"""

    def __init__(self):
        self.query_processor = HRQueryProcessor()

    def retrieve_context(self, query: str, user_role: str = "hr_lead", max_context_length: int = 3000) -> Tuple[str, Dict[str, Any]]:
        """
        Retrieve relevant context based on query analysis with role-based filtering

        Args:
            query: The user's question
            user_role: "hr_lead" (full access) or "hr_junior" (restricted access)
            max_context_length: Maximum context length in characters

        Returns:
            Tuple of (context_string, metadata_dict)
        """
        # Classify the query
        query_types = self.query_processor.classify_query(query)
        metadata = {
            "query_types": query_types,
            "sources_used": [],
            "access_restricted": False,
            "user_role": user_role
        }

        # Check if junior HR is trying to access restricted data
        if user_role == "hr_junior" and self.query_processor.is_sensitive_query(query, query_types):
            context = """=== ACCESS RESTRICTED ===

This query requests information that requires HR Lead permissions.

You have Junior HR access, which allows you to view:
- Benefits information (health insurance, dental, vision plans)
- Company policies (PTO, sick days, holidays)
- Aggregate statistics (employee counts, visa type distributions)
- General employee information (position, join date - without salary details)

Restricted information (HR Lead only):
- Individual employee salaries and compensation
- Specific visa expiration dates
- Termination records and dates

Please contact an HR Lead if you need access to this information."""

            metadata["access_restricted"] = True
            metadata["sources_used"].append("Access Control")
            return context, metadata

        context_parts = []

        # Extract specific information from query
        employee_ids = self.query_processor.extract_employee_ids(query)
        timeframe = self.query_processor.extract_timeframe(query)
        visa_type = self.query_processor.extract_visa_type(query)
        job_role = self.query_processor.extract_job_role(query)

        # 1. Employee-specific queries
        if "EMPLOYEE_LOOKUP" in query_types or employee_ids:
            for emp_id in employee_ids:
                employee = db.get_employee_by_id(emp_id)
                if employee:
                    summary = employee.get('summary', 'No data available')

                    # Sanitize for junior HR
                    if user_role == "hr_junior":
                        summary = self.query_processor.sanitize_employee_summary(summary)

                    context_parts.append(f"=== EMPLOYEE {emp_id} INFORMATION ===\n{summary}")
                    metadata["sources_used"].append(f"Employee {emp_id}")

        # 1.5 Job Role queries
        if "JOB_ROLE" in query_types and job_role:
            employees = db.search_employees_by_role(job_role)
            if employees:
                total_count = len(employees)

                context_parts.append(f"\n=== EMPLOYEES WITH ROLE: {job_role.upper()} ===")
                context_parts.append(f"TOTAL COUNT: {total_count} employees")
                # Show all employees up to 50 (to avoid context overflow)
                limit = min(total_count, 50)
                if limit < total_count:
                    context_parts.append(f"Showing first {limit} of {total_count} employees:")
                else:
                    context_parts.append(f"All {total_count} employees:")
                for emp in employees[:limit]:
                    summary = emp.get('summary', '')[:200]
                    # Sanitize for junior HR
                    if user_role == "hr_junior":
                        summary = self.query_processor.sanitize_employee_summary(summary)
                    context_parts.append(f"Employee {emp.get('employeeid')}: {summary}")
                metadata["sources_used"].append(f"Role: {job_role} ({total_count} total)")

        # 2. Visa and immigration queries
        if "VISA_STATUS" in query_types:
            # For statistics queries (e.g., "How many employees have H-1B?"),
            # ALWAYS use pre-calculated stats - these are OK for junior HR
            if "STATISTICS" in query_types:
                # Get accurate statistics from Possible Questions Summary
                possible_questions = db.get_possible_questions()
                if possible_questions:
                    context_parts.append("\n=== VISA STATISTICS (ACCURATE COUNTS) ===")
                    # Find visa-related statistics
                    for q in possible_questions:
                        summary = q.get('summary', '')
                        fields = q.get('fields', '')
                        if any(keyword in summary.lower() or keyword in fields.lower()
                               for keyword in ['visa', 'h-1b', 'h1b', 'green card', 'opt', 'cpt', 'citizen']):
                            context_parts.append(f"- {summary}")
                    metadata["sources_used"].append("Visa Statistics")
            elif visa_type:
                # Get employees with specific visa type (for non-statistics queries)
                employees = db.get_employees_with_visa_type(visa_type)
                if employees:
                    context_parts.append(f"\n=== EMPLOYEES WITH {visa_type.upper()} ===")
                    for emp in employees[:10]:  # Limit to 10
                        summary = emp.get('summary', '')[:300]
                        # Sanitize for junior HR - hide expiration dates
                        if user_role == "hr_junior":
                            summary = self.query_processor.sanitize_employee_summary(summary)
                        context_parts.append(f"Employee {emp.get('employeeid')}: {summary}")
                    metadata["sources_used"].append(f"Visa Type: {visa_type}")
            else:
                # General visa information (not a statistics query)
                sample_employees = db.get_all_employees(limit=5)
                visa_info = [emp for emp in sample_employees if "Visa type:" in emp.get("summary", "")]
                if visa_info:
                    context_parts.append("\n=== VISA INFORMATION SAMPLES ===")
                    for emp in visa_info:
                        summary = emp.get('summary', '')[:300]
                        # Sanitize for junior HR
                        if user_role == "hr_junior":
                            summary = self.query_processor.sanitize_employee_summary(summary)
                        context_parts.append(f"Employee {emp.get('employeeid')}: {summary}")
                    metadata["sources_used"].append("Visa samples")

        # 3. Benefits queries - OK for all roles
        if "BENEFITS" in query_types:
            # Health insurance
            if any(word in query.lower() for word in ["health", "medical", "insurance"]):
                medical_plans = db.get_medical_plans()
                if medical_plans:
                    context_parts.append("\n=== MEDICAL INSURANCE PLANS ===")
                    for plan in medical_plans[:2]:
                        context_parts.append(str(plan)[:500])
                    metadata["sources_used"].append("Medical Plans")

            # Dental
            if "dental" in query.lower():
                dental = db.get_dental_benefits()
                if dental:
                    context_parts.append("\n=== DENTAL BENEFITS ===")
                    context_parts.append(str(dental)[:500])
                    metadata["sources_used"].append("Dental Benefits")

            # Vision
            if "vision" in query.lower():
                vision = db.get_vision_benefits()
                if vision:
                    context_parts.append("\n=== VISION BENEFITS ===")
                    context_parts.append(str(vision)[:500])
                    metadata["sources_used"].append("Vision Benefits")

        # 4. Policy queries - OK for all roles
        if "POLICY" in query_types:
            agreement = db.get_employment_agreement()
            if agreement:
                context_parts.append("\n=== EMPLOYMENT POLICY ===")
                agreement_text = agreement.get("content", "")
                # Extract relevant sections
                if any(word in query.lower() for word in ["sick", "vacation", "pto", "holiday", "time off", "leave"]):
                    context_parts.append(f"PTO/Leave Policy: {agreement_text[:800]}")
                    metadata["sources_used"].append("Employment Agreement")

        # 5. Statistics and aggregate queries - OK for all roles
        if "STATISTICS" in query_types:
            possible_questions = db.get_possible_questions()
            if possible_questions:
                context_parts.append("\n=== AVAILABLE STATISTICS ===")
                for q in possible_questions[:5]:
                    context_parts.append(f"- {q.get('question', '')}: {q.get('summary', '')}")
                metadata["sources_used"].append("Statistics")

        # 6. General employment information
        if "EMPLOYMENT_INFO" in query_types and not employee_ids:
            # Get sample employees
            employees = db.get_all_employees(limit=3)
            context_parts.append("\n=== EMPLOYMENT INFORMATION SAMPLES ===")
            for emp in employees:
                summary = emp.get('summary', '')[:200]
                # Sanitize for junior HR
                if user_role == "hr_junior":
                    summary = self.query_processor.sanitize_employee_summary(summary)
                context_parts.append(f"Employee {emp.get('employeeid')}: {summary}")
            metadata["sources_used"].append("Employee samples")

        # Fallback: if no specific context found, get general info
        if not context_parts:
            context_parts.append("=== GENERAL HR INFORMATION ===")
            context_parts.append("I have access to employee records, visa information, benefits details, and company policies.")
            possible_q = db.get_possible_questions()
            if possible_q:
                context_parts.append("\nCommon questions I can help with:")
                for q in possible_q[:3]:
                    context_parts.append(f"- {q.get('question', '')}")
            metadata["sources_used"].append("General information")

        # Combine and limit context length
        full_context = "\n".join(context_parts)
        if len(full_context) > max_context_length:
            full_context = full_context[:max_context_length] + "\n... (context truncated)"

        return full_context, metadata


# Global RAG pipeline instance
rag = RAGPipeline()

# Testing
if __name__ == "__main__":
    print("Testing RAG Pipeline with Role-Based Access Control...")
    db.connect()

    test_queries = [
        ("What is the visa status of employee 1503?", "hr_lead"),
        ("What is the salary of employee 1503?", "hr_junior"),  # Should be blocked
        ("What is the salary of employee 1503?", "hr_lead"),    # Should work
        ("How many employees have H-1B visas?", "hr_junior"),   # Statistics - OK
        ("Tell me about our health insurance plans", "hr_junior"),  # Benefits - OK
        ("What are the sick day and vacation policies?", "hr_junior"),  # Policy - OK
    ]

    for query, role in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"Role: {role}")
        context, metadata = rag.retrieve_context(query, user_role=role)
        print(f"Query Types: {metadata['query_types']}")
        print(f"Access Restricted: {metadata.get('access_restricted', False)}")
        print(f"Sources: {metadata['sources_used']}")
        print(f"Context Preview: {context[:300]}...")
