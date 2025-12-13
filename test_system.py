from app import app, db
from models import Student, Attendance
from datetime import datetime

def test_system():
    with app.app_context():
        print("Creating database...")
        db.create_all()
        
        print("Testing Student Creation...")
        if not Student.query.filter_by(student_id="TEST001").first():
            s = Student(name="Test Student", student_id="TEST001", qr_code_path="static/qrcodes/TEST001.png")
            db.session.add(s)
            db.session.commit()
            print("Student created.")
        else:
            print("Student already exists.")
            
        print("Testing Attendance Marking...")
        a = Attendance(student_id="TEST001")
        db.session.add(a)
        db.session.commit()
        print("Attendance marked.")
        
        print("Verifying records...")
        count = Attendance.query.filter_by(student_id="TEST001").count()
        print(f"Total attendance records for TEST001: {count}")
        
        print("System test passed!")

if __name__ == "__main__":
    test_system()
