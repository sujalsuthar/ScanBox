from app import create_app
import os

# Create the Flask app instance for Vercel
app = create_app(os.getenv('FLASK_ENV', 'production'))

# Vercel requires this
if __name__ == "__main__":
    app.run()
