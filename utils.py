import qrcode
import os
import threading
from app import app, mail
from flask_mail import Message
from PIL import Image, ImageDraw, ImageFont
from typing import Optional

def generate_qr(student_id: str) -> str:
    """
    Generates a QR code for the given student_id and saves it.
    Returns the relative path to the QR code image.
    
    Args:
        student_id (str): The ID of the student.
        
    Returns:
        str: Relative path to the generated QR code image.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(student_id)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    filename = f"{student_id}.png"
    # Save in static/qrcodes
    filepath = os.path.join(app.root_path, 'static', 'qrcodes', filename)
    img.save(filepath)
    
    return f"static/qrcodes/{filename}"

def generate_id_card(student) -> str:
    """
    Generates a simple ID card for the student.
    
    Args:
        student (Student): The student object.
        
    Returns:
        str: Relative path to the generated ID card image.
    """
    # Create a blank white card
    width, height = 600, 350
    card = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(card)
    
    # Draw Header
    draw.rectangle([(0, 0), (width, 80)], fill='#4e54c8')
    
    # Load Font (default if specific font not found)
    try:
        font_header = ImageFont.truetype("arial.ttf", 40)
        font_text = ImageFont.truetype("arial.ttf", 25)
        font_small = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font_header = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_small = ImageFont.load_default()
        
    # Draw Text
    draw.text((300, 20), "STUDENT ID CARD", fill='white', font=font_header, anchor="mt")
    
    draw.text((50, 120), f"Name: {student.name}", fill='black', font=font_text)
    draw.text((50, 170), f"ID: {student.student_id}", fill='black', font=font_text)
    draw.text((50, 220), "Smart Attendance System", fill='gray', font=font_small)
    
    # Paste QR Code
    qr_path = os.path.join(app.root_path, student.qr_code_path)
    if os.path.exists(qr_path):
        qr_img = Image.open(qr_path).resize((150, 150))
        card.paste(qr_img, (400, 100))
        
    # Save ID Card
    filename = f"id_{student.student_id}.png"
    filepath = os.path.join(app.root_path, 'static', 'qrcodes', filename)
    card.save(filepath)
    
    return f"static/qrcodes/{filename}"

def send_async_email(subject: str, recipient: str, body: str) -> None:
    """
    Sends an email asynchronously using a separate thread.
    
    Args:
        subject (str): Email subject.
        recipient (str): Email recipient address.
        body (str): Email body text.
    """
    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient])
    msg.body = body
    
    def _send_async(app, msg):
        with app.app_context():
            try:
                mail.send(msg)
                print(f"ASYNC EMAIL SENT: {msg.subject}")
            except Exception as e:
                print(f"ASYNC EMAIL FAILED: {e}")
                
    thread = threading.Thread(target=_send_async, args=(app, msg))
    thread.start()
