import os
import logging
import json
from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Add custom Jinja2 filter to parse JSON strings
@app.template_filter('fromjson')
def fromjson_filter(value):
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return {}

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.get_by_id(user_id)

# Ensure required CSV files exist
from csv_models import ensure_files_exist
ensure_files_exist()

# Seed the database with initial data
def seed_data():
    from models import User, Event, EventRegistration
    from datetime import datetime
    import csv_models as cm

    if not User.get_all():
        logger.info("Seeding initial data...")

        # Admin user
        admin = User(
            username='admin',
            email='admin@alumni.org',
            first_name='Admin',
            last_name='User',
            graduation_year=2010,
            is_admin=True
        )
        admin.set_password('adminpass')
        admin.save()

        # Test user
        test_user = User(
            username='testuser',
            email='test@alumni.org',
            first_name='Test',
            last_name='User',
            graduation_year=2020,
            is_admin=False
        )
        test_user.set_password('testpass')
        test_user.save()

        # Create events
        future_year = datetime.now().year + 1
        events = [
            Event(
                title='Annual Alumni Reunion',
                description='Networking and guest speakers.',
                date=datetime(future_year, 12, 15, 18, 0, 0),
                location='University Main Hall'
            ),
            Event(
                title='Career Workshop',
                description='Career skills for modern workplace.',
                date=datetime(future_year, 12, 5, 14, 0, 0),
                location='Business School, Room 302'
            ),
            Event(
                title='Homecoming Game',
                description='Football game against rivals.',
                date=datetime(future_year, 11, 20, 15, 0, 0),
                location='University Stadium'
            )
        ]

        for event in events:
            event.save()

        logger.info("Seed data created successfully")

seed_data()


# === Import remaining routes ===
from routes import *
