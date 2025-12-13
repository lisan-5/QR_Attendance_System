import pytest
from app import app, db
from models import User, Student, Course

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create Admin
            admin = User(username='admin', password='admin123')
            db.session.add(admin)
            db.session.commit()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def auth_client(client):
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    return client
