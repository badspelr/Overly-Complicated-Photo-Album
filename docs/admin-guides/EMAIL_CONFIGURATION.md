# Email Configuration Guide

## Current Status

**Email IS Working** - but only in **Console Mode** (development)

When `DEBUG = True` (which it currently is), emails are printed to Docker logs instead of being sent via SMTP. This is intentional for development to avoid accidental email sending.

## Evidence from Logs

```
Subject: Invitation to view albums
From: noreply@example.com
To: dannielsen65@gmail.com
Date: Wed, 22 Oct 2025 19:35:50 -0000

Hello!
amandanielsen221@gmail.com has invited you to view their albums...
```

This shows the email system is working - it's just not sending actual emails yet.

## How Email Backend Works

**File:** `photo_album/settings.py` (lines 110-124)

```python
# Email configuration
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='webmaster@localhost')
CONTACT_EMAIL = config('CONTACT_EMAIL', default=DEFAULT_FROM_EMAIL)
EMAIL_SUBJECT_PREFIX = '[Photo Album] '

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Prints to console
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'    # Sends real emails
    EMAIL_HOST = config('EMAIL_HOST')
    EMAIL_PORT = config('EMAIL_PORT', cast=int)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
    SERVER_EMAIL = config('SERVER_EMAIL', default=EMAIL_HOST_USER)
```

## Email Features in the App

The app sends emails in these situations:

1. **User Invitations** (`/users/invite/`) - Invite users to view albums
2. **Contact Form** (`/contact/`) - Users submit contact messages to admins
3. **User Registration** (API) - Welcome emails to new users

## To Enable Real Email Sending

### Option 1: Keep Development Mode (Recommended for Testing)
**Do nothing** - emails will continue to print to Docker logs, which is safe for development.

To view emails:
```bash
docker-compose logs -f web | grep -A 20 "Subject:"
```

### Option 2: Enable SMTP for Real Email Delivery

#### Step 1: Choose an Email Provider

**Gmail (Personal):**
- Free for low volume
- Requires App Password (not regular password)
- Daily limit: 500 emails

**Gmail Workspace/Google Workspace:**
- Better for production
- Higher limits
- Same SMTP settings as personal Gmail

**SendGrid:**
- Free tier: 100 emails/day
- Easy API integration
- Good for production

**Amazon SES:**
- Very cheap ($0.10 per 1000 emails)
- Requires AWS account
- Best for high volume

**Mailgun:**
- Free tier: 5,000 emails/month
- Developer-friendly
- Good documentation

#### Step 2: Get SMTP Credentials

**For Gmail:**
1. Go to Google Account → Security
2. Enable 2-Factor Authentication
3. Generate an "App Password" for "Mail"
4. Use this password (not your regular password)

**For SendGrid:**
1. Sign up at sendgrid.com
2. Create an API key
3. Use API key as password

#### Step 3: Create/Update `.env` File

Create or edit `.env` in the project root:

```env
# Debug mode (set to False for production)
DEBUG=False

# Email Settings
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
CONTACT_EMAIL=admin@yourdomain.com

# SMTP Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
EMAIL_USE_TLS=True
SERVER_EMAIL=server@yourdomain.com
```

**For Gmail:**
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=youremail@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx  # App Password (16 chars)
EMAIL_USE_TLS=True
```

**For SendGrid:**
```env
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxx  # Your SendGrid API key
EMAIL_USE_TLS=True
```

**For Amazon SES:**
```env
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_HOST_USER=AKIA...  # Your SMTP username
EMAIL_HOST_PASSWORD=xxxx  # Your SMTP password
EMAIL_USE_TLS=True
```

#### Step 4: Update Docker Configuration

The `.env` file should be in the same directory as `docker-compose.yml`. Docker Compose automatically reads it.

Restart the container:
```bash
docker-compose restart web
```

#### Step 5: Test Email Sending

**Method 1: Django Shell**
```bash
docker exec -it photo_album_web python manage.py shell
```

Then in the shell:
```python
from django.core.mail import send_mail
send_mail(
    'Test Email',
    'This is a test email from Photo Album.',
    'noreply@yourdomain.com',
    ['your-email@gmail.com'],
    fail_silently=False,
)
```

**Method 2: Use Contact Form**
1. Go to http://localhost:8000/contact/
2. Fill out the form
3. Submit
4. Check your email inbox

## Troubleshooting

### "SMTPAuthenticationError"
- **Gmail:** Make sure you're using an App Password, not your regular password
- Verify 2FA is enabled on your Google account
- Check username is your full email address

### "Connection refused" or "Connection timed out"
- Check EMAIL_PORT (587 for TLS, 465 for SSL)
- Verify EMAIL_USE_TLS is True
- Check firewall isn't blocking SMTP ports

### "SMTPSenderRefused"
- Email address in DEFAULT_FROM_EMAIL must match EMAIL_HOST_USER (for most providers)
- Or use a verified sender email

### Emails go to spam
- Add SPF/DKIM records to your domain DNS
- Use a custom domain instead of Gmail
- Consider a dedicated email service like SendGrid

### Still printing to console
- Make sure `DEBUG=False` in `.env`
- Restart Docker: `docker compose restart web`
- Verify .env is in the right location (same dir as docker-compose.yml)

## Development vs Production

**Development (Current):**
- `DEBUG=True`
- `EMAIL_BACKEND=console.EmailBackend`
- Emails print to Docker logs
- Safe for testing without sending real emails

**Production:**
- `DEBUG=False`
- `EMAIL_BACKEND=smtp.EmailBackend`
- Emails sent via SMTP
- Requires valid SMTP credentials

## Viewing Console Emails

When in development mode, view emails in Docker logs:

```bash
# Follow logs in real-time
docker-compose logs -f web

# Search for emails
docker-compose logs web | grep -A 30 "Subject:"

# Last 100 lines
docker-compose logs --tail=100 web

# Filter for email content
docker-compose logs web | grep -E "(Subject|From|To|Content-Type)" -A 5
```

## Security Considerations

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Use App Passwords** - Not your main account password
3. **Rotate credentials** - Change passwords periodically
4. **Monitor usage** - Check for unusual email activity
5. **Rate limiting** - Be aware of provider limits

## Recommended Setup

**For Development:**
- Keep `DEBUG=True`
- Use console backend
- View emails in logs

**For Production:**
- Set `DEBUG=False`
- Use SendGrid or Amazon SES
- Configure proper sender domain
- Add SPF/DKIM records
- Monitor delivery rates

## Summary

Your email system is **working correctly** - it's just in development mode. To send real emails:

1. Choose an email provider (Gmail, SendGrid, etc.)
2. Get SMTP credentials
3. Add them to `.env` file
4. Set `DEBUG=False`
5. Restart Docker container
6. Test with contact form or Django shell

For now, you can test the email functionality by checking Docker logs:
```bash
docker-compose logs -f web | grep -B 5 -A 20 "Subject:"
```

## Date
October 22, 2025
