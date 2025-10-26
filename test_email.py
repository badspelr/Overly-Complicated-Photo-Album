"""
Test email configuration for Django Photo Album.
This script tests the SMTP connection and attempts to send a test email.
"""

from django.core.mail import send_mail
from django.conf import settings
import smtplib
from email.mime.text import MIMEText

print("=" * 60)
print("Django Email Configuration Test")
print("=" * 60)

# Display current settings
print("\nCurrent Email Settings:")
print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"  EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
print(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"  EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'Not set'}")
print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print(f"  SERVER_EMAIL: {settings.SERVER_EMAIL}")

# Test 1: Direct SMTP connection
print("\n" + "=" * 60)
print("Test 1: Testing direct SMTP connection...")
print("=" * 60)
try:
    smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
    smtp.set_debuglevel(1)  # Show all SMTP communication
    print("✓ Connected to SMTP server")
    
    smtp.ehlo()
    print("✓ EHLO successful")
    
    if settings.EMAIL_USE_TLS:
        smtp.starttls()
        print("✓ STARTTLS successful")
        smtp.ehlo()
    
    if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        print("✓ Authentication successful")
    
    smtp.quit()
    print("✓ SMTP connection test PASSED")
except Exception as e:
    print(f"✗ SMTP connection test FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Django send_mail
print("\n" + "=" * 60)
print("Test 2: Testing Django send_mail()...")
print("=" * 60)

test_email = input("Enter email address to send test email to (or press Enter to skip): ").strip()

if test_email:
    try:
        send_mail(
            'Test Email from Photo Album',
            'This is a test email to verify SMTP configuration.\n\nIf you receive this, email is working correctly!',
            settings.DEFAULT_FROM_EMAIL,
            [test_email],
            fail_silently=False,
        )
        print(f"✓ Test email sent successfully to {test_email}")
        print("  Check the inbox (and spam folder) of the recipient")
    except Exception as e:
        print(f"✗ Failed to send test email: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Skipped send_mail test")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
