# app/__init__.py
"""
Email Scanner API - Professional Application Factory
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from app.config import config
from app.models.database import init_db, close_db

logger = logging.getLogger(__name__)


def create_app(config_name: str = None) -> Flask:
    """
    Application factory for creating and configuring Flask app.
    
    Args:
        config_name: Configuration environment ('development', 'production', 'testing')
    
    Returns:
        Configured Flask application instance
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Get the absolute path to templates folder (in project root, not in app/)
    import sys
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    app = Flask(
        __name__,
        template_folder=os.path.join(root_dir, 'templates'),
        static_folder=os.path.join(root_dir, 'templates', 'static')
    )
    
    # Load configuration
    config_class = config[config_name]
    app.config.from_object(config_class)
    
    # Validate production config
    if config_name == 'production':
        config_class.validate()
    
    # Setup logging
    setup_logging(app)
    
    # Enable CORS for frontend access
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Initialize database
    init_db(app)
    
    # Initialize user tables
    from app.models.user import User
    User.init_table()
    
    # Register cleanup
    app.teardown_appcontext(close_db)
    
    # Register authentication blueprint (after models initialized)
    from app.auth import auth_bp
    from app.auth import routes as auth_routes  # noqa
    app.register_blueprint(auth_bp)
    
    # Register enterprise feature blueprints
    from app.admin import admin_bp
    from app.reporting import reporting_bp
    from app.siem import siem_bp
    from app.policy import policy_bp
    from app.tenant import tenant_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(reporting_bp)
    app.register_blueprint(siem_bp)
    app.register_blueprint(policy_bp)
    app.register_blueprint(tenant_bp)
    
    # Register API routes (import deferred to avoid circular import)
    from app.api.routes import register_routes
    register_routes(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    logger.info(f"Flask app created with config: {config_name}")
    return app


def setup_logging(app: Flask) -> None:
    """
    Configure application logging.
    
    Args:
        app: Flask application instance
    """
    if not app.debug:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)


def register_error_handlers(app: Flask) -> None:
    """
    Register error handlers for common HTTP errors.
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(400)
    def bad_request(error):
        return {
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }, 400
    
    @app.errorhandler(404)
    def not_found(error):
        return {
            'error': 'Not Found',
            'message': 'The requested resource does not exist'
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal server error: {error}')
        return {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }, 500
