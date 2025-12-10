#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Email Scanner - Professional Application Entry Point
"""

import os
import logging
import sys
from app import create_app

# Configure logging before app creation
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log') if not os.getenv('FLASK_ENV') == 'development' else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """
    Application entry point.
    """
    # Get configuration from environment or use default
    config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create application
    app = create_app(config_name=config_name)
    
    # Determine host and port
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = config_name == 'development'
    
    logger.info(f"Starting Email Scanner API")
    logger.info(f"Environment: {config_name}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Server: http://{host}:{port}")
    
    if debug:
        logger.info("Starting development server...")
        logger.info("Open browser: http://127.0.0.1:5000")
        logger.info("Press CTRL+C to stop")
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug
        )
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
