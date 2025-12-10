"""Authentication routes for login, register, and token management"""

from flask import request, jsonify
from app.auth import auth_bp
from app.auth.utils import AuthUtils, require_auth
from app.models.user import User
from app.utils.validators import Validator
import logging

logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validate
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        if not Validator.validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Create user
        result = User.create_user(email, password)
        
        if not result['success']:
            return jsonify({'error': result.get('error', 'Registration failed')}), 400
        
        logger.info(f"User registered: {email}")
        return jsonify({
            'message': 'User registered successfully',
            'user_id': result['id'],
            'email': result['email']
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Verify credentials
        result = User.verify_credentials(email, password)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 401
        
        # Generate tokens
        access_token = AuthUtils.create_access_token(result['user_id'], email)
        refresh_token = AuthUtils.create_refresh_token(result['user_id'])
        
        logger.info(f"User logged in: {email}")
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': result['user_id'],
            'email': email,
            'is_admin': result.get('is_admin', False)
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token using refresh token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token', '')
        
        if not refresh_token:
            return jsonify({'error': 'Refresh token required'}), 400
        
        payload = AuthUtils.verify_token(refresh_token)
        
        if not payload or payload.get('type') != 'refresh':
            return jsonify({'error': 'Invalid refresh token'}), 401
        
        user_id = payload.get('user_id')
        user = User.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate new access token
        new_access_token = AuthUtils.create_access_token(user_id, user['email'])
        
        return jsonify({
            'access_token': new_access_token,
            'token_type': 'Bearer'
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({'error': 'Token refresh failed'}), 500

@auth_bp.route('/verify', methods=['GET'])
@require_auth
def verify_token():
    """Verify current authentication status"""
    try:
        user = User.get_user_by_id(request.user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'authenticated': True,
            'user_id': user['user_id'],
            'email': user['email'],
            'is_admin': user['is_admin'],
            'last_login': user['last_login']
        }), 200
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({'error': 'Verification failed'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not old_password or not new_password:
            return jsonify({'error': 'Old and new passwords required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
        user = User.get_user_by_id(request.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify old password
        result = User.verify_credentials(user['email'], old_password)
        if not result['success']:
            return jsonify({'error': 'Incorrect old password'}), 401
        
        # Update password
        if User.update_password(request.user_id, new_password):
            logger.info(f"Password changed for user: {user['email']}")
            return jsonify({'message': 'Password changed successfully'}), 200
        else:
            return jsonify({'error': 'Failed to change password'}), 500
        
    except Exception as e:
        logger.error(f"Change password error: {e}")
        return jsonify({'error': 'Password change failed'}), 500

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get user profile"""
    try:
        user = User.get_user_by_id(request.user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user_id': user['id'],
            'email': user['email'],
            'is_admin': user['is_admin'],
            'is_active': user['is_active'],
            'created_at': user['created_at'],
            'last_login': user['last_login']
        }), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500
