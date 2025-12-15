"""
Role-Based Authentication for HR Chatbot
Supports two roles: hr_lead (full access) and hr_junior (restricted access)
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Security scheme
security = HTTPBasic()

class AuthRequest(BaseModel):
    """Authentication request model"""
    username: str
    password: str

class AuthResponse(BaseModel):
    """Authentication response model"""
    authenticated: bool
    message: str
    username: Optional[str] = None
    role: Optional[str] = None  # "hr_lead" or "hr_junior"

def get_chatbot_password() -> str:
    """Get the legacy chatbot password from environment variable"""
    return os.getenv("CHATBOT_PASSWORD", "hr2025")

def load_users_config() -> Dict[str, Dict[str, str]]:
    """
    Load user configurations from environment variable
    Expected format in .env:
    HR_USERS={"alice": {"password": "lead123", "role": "hr_lead"}, "bob": {"password": "junior456", "role": "hr_junior"}}
    """
    users_json = os.getenv("HR_USERS", "{}")
    try:
        users = json.loads(users_json)
        return users
    except json.JSONDecodeError:
        print("Warning: Failed to parse HR_USERS config, using empty user list")
        return {}

def verify_credentials(username: str, password: str) -> Optional[Dict[str, str]]:
    """
    Verify username and password, return user info if valid
    Returns: {"username": "...", "role": "hr_lead|hr_junior"} or None
    """
    users = load_users_config()
    if username in users:
        user_data = users[username]
        if user_data.get("password") == password:
            role = user_data.get("role", "hr_junior")  # Default to junior for safety
            # Validate role
            if role not in ["hr_lead", "hr_junior"]:
                role = "hr_junior"
            return {
                "username": username,
                "role": role
            }
    return None

def verify_password(password: str) -> bool:
    """
    Legacy password-only verification (backward compatibility)
    Returns True if password matches the legacy CHATBOT_PASSWORD
    """
    correct_password = get_chatbot_password()
    return password == correct_password

async def authenticate(username: str, password: str) -> AuthResponse:
    """Authenticate user with username and password"""
    user_info = verify_credentials(username, password)

    if user_info:
        return AuthResponse(
            authenticated=True,
            message="Authentication successful",
            username=user_info["username"],
            role=user_info["role"]
        )
    else:
        return AuthResponse(
            authenticated=False,
            message="Invalid username or password"
        )

def check_authentication(password: str) -> bool:
    """Check if password is correct (legacy, for backward compatibility)"""
    return verify_password(password)
