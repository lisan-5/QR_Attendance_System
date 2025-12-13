from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from app import app, db, mail
from models import Student, Attendance, User, Course
from utils import generate_qr, generate_id_card
from datetime import datetime, timedelta
from flask_login import login_user, login_required, logout_user, current_user
from fpdf import FPDF
from flask_mail import Message
import pandas as pd
import io
import os

# ... (Previous routes remain unchanged until mark_attendance) ...

@app.route('/')
@login_required
def index():
    total_students = Student.query.count()
    total_attendance_today = Attendance.query.filter(
        db.func.date(Attendance.timestamp) == datetime.utcnow().date()
    ).count()
    
    # Get recent attendance
    recent_attendance = Attendance.query.order_by(Attendance.timestamp.desc()).limit(10).all()
    
    # Data for Chart.js (Last 7 days)
    dates = []
    counts = []
    for i in range(6, -1, -1):
        date = datetime.utcnow().date() - timedelta(days=i)
        count = Attendance.query.filter(db.func.date(Attendance.timestamp) == date).count()
        dates.append(date.strftime('%Y-%m-%d'))
        counts.append(count)
        
    return render_template('index.html', 
                           total_students=total_students, 
                           total_attendance_today=total_attendance_today,
                           recent_attendance=recent_attendance,
                           chart_dates=dates,
                           chart_counts=counts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            app.logger.info(f'Admin login: {username}')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
            app.logger.warning(f'Failed login attempt: {username}')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        student_id = request.form.get('student_id')
        
        if Student.query.filter_by(student_id=student_id).first():
            flash('Student ID already exists!', 'danger')
            return redirect(url_for('register'))
        
        qr_path = generate_qr(student_id)
        
        new_student = Student(name=name, student_id=student_id, qr_code_path=qr_path)
        db.session.add(new_student)
        db.session.commit()
        
        # Generate ID Card immediately
        generate_id_card(new_student)
        
        app.logger.info(f'New student registered: {name} ({student_id})')
        flash('Student registered successfully!', 'success')
        return redirect(url_for('index'))
        
    return render_template('register.html')

@app.route('/import_students', methods=['GET', 'POST'])
@login_required
def import_students():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            try:
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                count = 0
                for index, row in df.iterrows():
                    name = row.get('Name')
                    student_id = str(row.get('ID'))
                    
                    if name and student_id:
                        if not Student.query.filter_by(student_id=student_id).first():
                            qr_path = generate_qr(student_id)
                            new_student = Student(name=name, student_id=student_id, qr_code_path=qr_path)
                            db.session.add(new_student)
                            generate_id_card(new_student)
                            count += 1
                
                db.session.commit()
                app.logger.info(f'Bulk import: {count} students added')
                flash(f'Successfully imported {count} students!', 'success')
                return redirect(url_for('index'))
                
            except Exception as e:
                app.logger.error(f'Import failed: {str(e)}')
                flash(f'Error importing file: {str(e)}', 'danger')
        else:
            flash('Invalid file type. Please upload CSV or Excel.', 'danger')
            
    return render_template('import.html')

@app.route('/courses', methods=['GET', 'POST'])
@login_required
def courses():
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        
        if Course.query.filter_by(code=code).first():
            flash('Course code already exists!', 'danger')
        else:
            new_course = Course(name=name, code=code)
            db.session.add(new_course)
            db.session.commit()
            flash('Course added successfully!', 'success')
            
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)

@app.route('/scan')
@login_required
def scan_page():
    courses = Course.query.all()
    return render_template('scan.html', courses=courses)

@app.route('/api/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    
    if not student_id:
        return jsonify({'status': 'error', 'message': 'No Student ID provided'}), 400
        
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return jsonify({'status': 'error', 'message': 'Student not found'}), 404
        
    # Check for duplicate scan within last 5 minutes for the SAME course
    last_attendance = Attendance.query.filter_by(student_id=student_id, course_id=course_id).order_by(Attendance.timestamp.desc()).first()
    
    if last_attendance:
        time_diff = datetime.utcnow() - last_attendance.timestamp
        if time_diff < timedelta(minutes=5):
            return jsonify({'status': 'warning', 'message': 'Attendance already marked recently!'}), 200

    new_attendance = Attendance(student_id=student_id, course_id=course_id)
    db.session.add(new_attendance)
    db.session.commit()
    
    app.logger.info(f'Attendance marked: {student.name} ({student_id})')
    
    # Send Async Email Notification
    from utils import send_async_email
    subject = f"Attendance Marked: {student.name}"
    body = f"Hello {student.name},\n\nYour attendance has been marked for {datetime.utcnow()}."
    send_async_email(subject, "admin@attendance.com", body)
    
    return jsonify({'status': 'success', 'message': f'Attendance marked for {student.name}'}), 200

# ... (Export routes remain unchanged) ...

@app.route('/export')
@login_required
def export_attendance():
    records = Attendance.query.all()
    data = []
    for r in records:
        course_code = r.course.code if r.course else "N/A"
        data.append({
            'Student ID': r.student_id,
            'Name': r.student.name,
            'Course': course_code,
            'Timestamp': r.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    output.seek(0)
    
    return send_file(output, download_name="attendance_report.xlsx", as_attachment=True)

@app.route('/export/pdf')
@login_required
def export_pdf():
    records = Attendance.query.all()
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Attendance Report", ln=True, align='C')
    pdf.ln(10)
    
    # Header
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(40, 10, "Student ID", 1, 0, 'C', 1)
    pdf.cell(60, 10, "Name", 1, 0, 'C', 1)
    pdf.cell(40, 10, "Course", 1, 0, 'C', 1)
    pdf.cell(50, 10, "Time", 1, 1, 'C', 1)
    
    # Rows
    for r in records:
        course_code = r.course.code if r.course else "N/A"
        pdf.cell(40, 10, r.student_id, 1)
        pdf.cell(60, 10, r.student.name, 1)
        pdf.cell(40, 10, course_code, 1)
        pdf.cell(50, 10, r.timestamp.strftime('%Y-%m-%d %H:%M'), 1, 1)
        
    output = io.BytesIO()
    # Output to string first, then encode to bytes
    pdf_content = pdf.output(dest='S').encode('latin-1')
    output.write(pdf_content)
    output.seek(0)
    
    return send_file(output, download_name="attendance_report.pdf", as_attachment=True, mimetype='application/pdf')

@app.route('/download_id/<student_id>')
@login_required
def download_id(student_id):
    filename = f"id_{student_id}.png"
    filepath = os.path.join(app.root_path, 'static', 'qrcodes', filename)
    
    # Regenerate if missing
    if not os.path.exists(filepath):
        student = Student.query.filter_by(student_id=student_id).first()
        if student:
            generate_id_card(student)
            
    return send_file(filepath, as_attachment=True)

@app.route('/analytics')
@login_required
def analytics():
    # Calculate attendance % per student
    students = Student.query.all()
    data = []
    
    # Assume total classes = unique dates * courses (Simplified logic for demo)
    # Better logic: Track total sessions per course. For now, we'll just show raw counts.
    
    for s in students:
        total_attended = len(s.attendance_records)
        # Mock "Total Classes" as 20 for demo purposes to show %
        total_classes = 20 
        percentage = (total_attended / total_classes) * 100
        
        status = "Good"
        if percentage < 75:
            status = "At Risk"
            
        data.append({
            'name': s.name,
            'id': s.student_id,
            'attended': total_attended,
            'percentage': round(percentage, 1),
            'status': status
        })
        
    return render_template('analytics.html', students=data)
