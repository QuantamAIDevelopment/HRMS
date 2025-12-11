#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.email_service import email_service

def test_email():
    print("Testing email configuration...")
    print(f"SMTP Server: {email_service.smtp_server}")
    print(f"SMTP Port: {email_service.smtp_port}")
    print(f"SMTP Username: {email_service.smtp_username}")
    print(f"SMTP Password: {'***' if email_service.smtp_password else 'None'}")
    print(f"From Email: {email_service.from_email}")
    
    # Test sending email
    result = email_service.send_otp_email("mailhr100@gmail.com", "123456")
    print(f"Email send result: {result}")

if __name__ == "__main__":
    test_email()