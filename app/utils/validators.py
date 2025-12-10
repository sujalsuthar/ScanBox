# app/utils/validators.py
"""
Input validation and sanitization utilities.
"""

import re
from typing import Tuple, Any
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class Validator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email or not isinstance(email, str):
            return False, "Email must be a non-empty string"
        
        email = email.strip()
        if len(email) > 254:
            return False, "Email address is too long"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        return True, ""
    
    @staticmethod
    def validate_app_password(password: str) -> Tuple[bool, str]:
        """
        Validate Google App Password format (16 alphanumeric with spaces).
        
        Args:
            password: App password to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password or not isinstance(password, str):
            return False, "App password must be a non-empty string"
        
        # Remove spaces and check length
        clean_password = password.replace(" ", "")
        
        if len(clean_password) != 16:
            return False, "App password must be 16 characters (spaces are optional)"
        
        if not clean_password.isalnum():
            return False, "App password must contain only alphanumeric characters"
        
        return True, ""
    
    @staticmethod
    def validate_limit(limit: Any) -> Tuple[bool, str]:
        """
        Validate email scan limit.
        
        Args:
            limit: Number of emails to scan
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            limit_int = int(limit)
        except (ValueError, TypeError):
            return False, "Limit must be an integer"
        
        if limit_int < 1:
            return False, "Limit must be at least 1"
        
        if limit_int > 100:
            return False, "Limit cannot exceed 100 emails"
        
        return True, ""
    
    @staticmethod
    def validate_scan_request(data: dict) -> Tuple[bool, str]:
        """
        Validate complete scan request payload.
        
        Args:
            data: Request JSON data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Request body must be JSON object"
        
        # Check required fields
        if 'gmail' not in data:
            return False, "Missing required field: gmail"
        
        if 'app_password' not in data:
            return False, "Missing required field: app_password"
        
        # Validate email
        is_valid, error = Validator.validate_email(data['gmail'])
        if not is_valid:
            return False, f"Invalid gmail: {error}"
        
        # Validate app password
        is_valid, error = Validator.validate_app_password(data['app_password'])
        if not is_valid:
            return False, f"Invalid app_password: {error}"
        
        # Validate limit if provided
        if 'limit' in data:
            is_valid, error = Validator.validate_limit(data['limit'])
            if not is_valid:
                return False, f"Invalid limit: {error}"
        
        return True, ""


class Sanitizer:
    """Input sanitization utilities."""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 500) -> str:
        """
        Sanitize string input (strip whitespace, truncate, remove control chars).
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
        
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return ""
        
        # Remove control characters except newlines and tabs
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\t')
        
        # Strip whitespace
        value = value.strip()
        
        # Truncate if necessary
        if len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing dangerous characters.
        
        Args:
            filename: Filename to sanitize
        
        Returns:
            Sanitized filename
        """
        if not filename:
            return "unknown"
        
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Remove dangerous characters
        dangerous_chars = r'[<>:"|?*\x00-\x1f]'
        filename = re.sub(dangerous_chars, '', filename)
        
        # Truncate if too long
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:240] + ('.' + ext if ext else '')
        
        return filename or "unknown"
