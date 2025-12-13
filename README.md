# Smart Attendance System 📱

A modern, web-based attendance system using QR codes, built with Flask, OpenCV, and SQLite.

## Features 🚀

- **QR Code Generation**: Automatically generates unique QR codes for registered students.
- **Webcam Scanning**: Marks attendance instantly by scanning QR codes via the browser.
- **Admin Dashboard**: View real-time statistics, recent activity, and attendance trends.
- **Course Management**: Create courses and track attendance specifically for each subject.
- **Excel Export**: Download detailed attendance reports.
- **Secure**: Admin authentication and duplicate scan prevention (Time Lock).

## Tech Stack 🛠️

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript, Bootstrap 5
- **Database**: SQLite
- **Libraries**: `qrcode`, `opencv-python`, `pyzbar`, `pandas`, `openpyxl`, `Chart.js`

## Installation 📦

1.  **Clone the repository**
    ```bash
    git clone https://github.com/lisan-5/sqr_attendance_system.git
    cd qr_attendance_system
    ```

2.  **Create a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application**
    ```bash
    python app.py
    ```

5.  **Access the app**
    Open `http://127.0.0.1:5001` in your browser.

## Usage 📖

1.  **Login**: Default credentials are `admin` / `admin123`.
2.  **Setup**: Go to **Courses** to add subjects (e.g., "Math 101").
3.  **Register**: Add students to generate their QR codes.
4.  **Scan**: Open the **Scan QR** page, select a course, and scan the student's QR code.
5.  **Report**: Use **Export Report** to get the attendance data.

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
