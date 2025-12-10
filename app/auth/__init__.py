"""Authentication module for MailShield Pro"""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

