"""Authentication utilities for JWT, password hashing, and token management"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash

class AuthUtils:
    """Utility functions for authentication and authorization"""
    
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS = 30

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using werkzeug"""
        return generate_password_hash(password, method='pbkdf2:sha256')

    @staticmethod
    def verify_password(hashed_password: str, password: str) -> bool:
        """Verify a password against its hash"""
        return check_password_hash(hashed_password, password)

    @staticmethod
    def create_access_token(user_id: int, user_email: str) -> str:
        """Create JWT access token"""
        payload = {
            'user_id': user_id,
            'email': user_email,
            'exp': datetime.utcnow() + timedelta(minutes=AuthUtils.ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        return jwt.encode(payload, AuthUtils.SECRET_KEY, algorithm=AuthUtils.ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """Create JWT refresh token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=AuthUtils.REFRESH_TOKEN_EXPIRE_DAYS),
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        return jwt.encode(payload, AuthUtils.SECRET_KEY, algorithm=AuthUtils.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, AuthUtils.SECRET_KEY, algorithms=[AuthUtils.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def get_token_from_request() -> str:
        """Extract token from Authorization header"""
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None
        return auth_header[7:]  # Remove 'Bearer ' prefix

def require_auth(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = AuthUtils.get_token_from_request()
        
        if not token:
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        payload = AuthUtils.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Pass user info to the route
        request.user_id = payload.get('user_id')
        request.user_email = payload.get('email')
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check authentication
        token = AuthUtils.get_token_from_request()
        if not token:
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        payload = AuthUtils.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Check if user is admin (this would be expanded with DB check)
        request.user_id = payload.get('user_id')
        request.user_email = payload.get('email')
        request.is_admin = payload.get('is_admin', False)
        
        if not request.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
