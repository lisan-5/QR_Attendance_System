from models import Student, Course, Attendance

def test_login(client):
    response = client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    assert b'Dashboard' in response.data

def test_register_student(auth_client):
    response = auth_client.post('/register', data={'name': 'Test Student', 'student_id': 'TEST001'}, follow_redirects=True)
    assert b'Student registered successfully' in response.data
    assert Student.query.count() == 1

def test_create_course(auth_client):
    response = auth_client.post('/courses', data={'name': 'Math', 'code': 'MATH101'}, follow_redirects=True)
    assert b'Course added successfully' in response.data
    assert Course.query.count() == 1

def test_mark_attendance(auth_client):
    # Setup
    auth_client.post('/register', data={'name': 'Test Student', 'student_id': 'TEST001'})
    auth_client.post('/courses', data={'name': 'Math', 'code': 'MATH101'})
    
    course = Course.query.first()
    
    # Mark Attendance
    response = auth_client.post('/api/mark_attendance', json={
        'student_id': 'TEST001',
        'course_id': course.id
    })
    
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert Attendance.query.count() == 1

def test_duplicate_attendance(auth_client):
    # Setup
    auth_client.post('/register', data={'name': 'Test Student', 'student_id': 'TEST001'})
    auth_client.post('/courses', data={'name': 'Math', 'code': 'MATH101'})
    course = Course.query.first()
    
    # First Mark
    auth_client.post('/api/mark_attendance', json={'student_id': 'TEST001', 'course_id': course.id})
    
    # Second Mark (Should be warning)
    response = auth_client.post('/api/mark_attendance', json={'student_id': 'TEST001', 'course_id': course.id})
    
    assert response.status_code == 200
    assert response.json['status'] == 'warning'
    assert Attendance.query.count() == 1
