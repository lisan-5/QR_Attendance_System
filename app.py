from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os
import logging
from logging.handlers import RotatingFileHandler

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail Config (Console Backend for Demo)
app.config['MAIL_SERVER'] = 'smtp.gmail.com' # Mock
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-password'
app.config['MAIL_BACKEND'] = 'console' # Prints to console instead of sending

# Initialize Extensions
db = SQLAlchemy(app)
mail = Mail(app)

# Logging Configuration
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/attendance.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Smart Attendance Startup')

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Ensure directories exist
os.makedirs('static/qrcodes', exist_ok=True)
os.makedirs('static/css', exist_ok=True)

# Import routes after app initialization to avoid circular imports
from routes import *

import click

# ... (Previous code)

# CLI Commands
@app.cli.command("create-admin")
@click.argument("username")
@click.argument("password")
def create_admin(username, password):
    """Create an admin user."""
    from models import User
    if User.query.filter_by(username=username).first():
        print(f"User {username} already exists.")
    else:
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        print(f"Admin user {username} created successfully.")

@app.cli.command("seed-db")
def seed_db():
    """Seed the database with test data."""
    from models import Student, Course
    from utils import generate_qr, generate_id_card
    
    # Seed Courses
    courses = [("Mathematics", "MATH101"), ("Physics", "PHYS101"), ("Computer Science", "CS101")]
    for name, code in courses:
        if not Course.query.filter_by(code=code).first():
            db.session.add(Course(name=name, code=code))
            print(f"Added Course: {name}")
            
    # Seed Students
    students = [("Alice Smith", "S001"), ("Bob Jones", "S002"), ("Charlie Brown", "S003")]
    for name, sid in students:
        if not Student.query.filter_by(student_id=sid).first():
            qr_path = generate_qr(sid)
            s = Student(name=name, student_id=sid, qr_code_path=qr_path)
            db.session.add(s)
            generate_id_card(s)
            print(f"Added Student: {name}")
            
    db.session.commit()
    print("Database seeded successfully.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        from models import User
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin123') # Plain text for demo
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin / admin123")
            
    app.run(debug=True, port=5001)
