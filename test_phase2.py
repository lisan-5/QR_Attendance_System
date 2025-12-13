from app import app, db
from models import User, Course, Student, Attendance
from datetime import datetime

def test_phase2():
    with app.app_context():
        print("Creating database...")
        db.create_all()
        
        # 1. Test Admin Creation
        print("Testing Admin Creation...")
        if not User.query.filter_by(username='admin').first():
            u = User(username='admin', password='admin123')
            db.session.add(u)
            db.session.commit()
            print("Admin created.")
        else:
            print("Admin already exists.")
            
        # 2. Test Course Creation
        print("Testing Course Creation...")
        if not Course.query.filter_by(code='CS101').first():
            c = Course(name="Computer Science", code="CS101")
            db.session.add(c)
            db.session.commit()
            print("Course CS101 created.")
        else:
            print("Course CS101 already exists.")
            
        course = Course.query.filter_by(code='CS101').first()
        
        # 3. Test Student Creation (if not exists)
        if not Student.query.filter_by(student_id="TEST002").first():
            s = Student(name="Phase2 Student", student_id="TEST002", qr_code_path="static/qrcodes/TEST002.png")
            db.session.add(s)
            db.session.commit()
            print("Student TEST002 created.")
            
        # 4. Test Attendance with Course
        print("Testing Attendance with Course...")
        a = Attendance(student_id="TEST002", course_id=course.id)
        db.session.add(a)
        db.session.commit()
        print("Attendance marked for CS101.")
        
        # Verify
        record = Attendance.query.filter_by(student_id="TEST002").order_by(Attendance.id.desc()).first()
        if record.course.code == 'CS101':
            print("Verification Successful: Attendance linked to CS101.")
        else:
            print("Verification Failed: Course link missing.")

if __name__ == "__main__":
    test_phase2()
