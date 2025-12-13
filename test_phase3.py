from app import app, db
from models import Student
from utils import generate_id_card
import os

def test_phase3():
    with app.app_context():
        print("Testing ID Card Generation...")
        # Create a test student if not exists
        if not Student.query.filter_by(student_id="TEST_ID").first():
            s = Student(name="ID Card Test", student_id="TEST_ID", qr_code_path="static/qrcodes/TEST_ID.png")
            db.session.add(s)
            db.session.commit()
            
        student = Student.query.filter_by(student_id="TEST_ID").first()
        
        # Generate ID Card
        path = generate_id_card(student)
        print(f"ID Card generated at: {path}")
        
        # Verify file exists
        full_path = os.path.join(app.root_path, path)
        if os.path.exists(full_path):
            print("Verification Successful: ID Card file exists.")
        else:
            print("Verification Failed: ID Card file missing.")

if __name__ == "__main__":
    test_phase3()
