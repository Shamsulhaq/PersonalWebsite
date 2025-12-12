# Email Configuration Guide

This application supports sending emails for:
- **Contact message replies**: Reply to users who submit contact forms
- **Newsletter notifications**: Automatically notify subscribers when new blog posts are published

## Setup Instructions

### 1. Configure Environment Variables

Set the following environment variables before starting the server:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_NAME="Your Name"
```

### 2. Using .env File (Recommended)

Create a `.env` file in your project root:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=Your Name
```

Then install python-dotenv:

```bash
pip install python-dotenv
```

Add this to the top of `main.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

### 3. Gmail Setup

For Gmail, you need to use an **App Password** instead of your regular password:

1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Scroll down to "App passwords"
4. Generate a new app password for "Mail"
5. Use this generated password in your `SMTP_PASSWORD` variable

**Important:** Enable 2-Factor Authentication first to access App Passwords.

### 4. Other Email Providers

#### Outlook/Office 365
```env
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
```

#### Yahoo Mail
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

#### Custom SMTP Server
Check your email provider's documentation for SMTP settings.

## Features

### Contact Message Replies

1. Go to Admin Panel → Messages
2. Click on any message to view details
3. Use the reply form at the bottom to send a response
4. The sender will receive your reply via email
5. Optionally send yourself a copy

### Newsletter Notifications

When you publish a new blog post:
- All active newsletter subscribers automatically receive an email notification
- Email includes post title, excerpt, and a link to read more
- Sent in the background, doesn't block the admin interface
- Only sent when:
  - Creating a new post with "Published" status checked
  - Changing an existing draft to "Published"

### Email Settings Page

Visit **Admin Panel → Settings → Email Settings** to:
- View current configuration
- Send test emails to verify setup
- See configuration instructions

## Testing

Test your email configuration:

1. Go to Admin Panel → Settings → Email Settings
2. Enter your email address
3. Click "Send Test Email"
4. Check your inbox

## Troubleshooting

### "Email credentials not configured"
- Environment variables are not set
- Check that variables are exported before starting the server

### "Failed to send email"
- Verify SMTP server and port are correct
- Check username and password
- For Gmail, ensure you're using an App Password
- Check firewall/antivirus settings
- Some networks block port 587

### "Authentication failed"
- Incorrect username or password
- For Gmail, you must use an App Password, not your regular password
- Some providers require "Allow less secure apps" to be enabled

### Test Connection

You can test your SMTP connection from Python:

```python
import smtplib

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your-email@gmail.com', 'your-app-password')
    print("✓ Connection successful!")
    server.quit()
except Exception as e:
    print(f"✗ Error: {e}")
```

## Security Best Practices

1. **Never commit credentials** to version control
2. Add `.env` to `.gitignore`
3. Use App Passwords instead of main account passwords
4. Rotate passwords periodically
5. Use environment-specific credentials for production

## Production Deployment

For production environments:

1. Set environment variables through your hosting platform (Heroku, Railway, etc.)
2. Use secure credential management services
3. Consider using a dedicated email service (SendGrid, Mailgun) for better deliverability
4. Monitor email sending limits to avoid rate limiting

## Rate Limits

Be aware of email sending limits:

- **Gmail**: ~500 emails/day for regular accounts, 2000/day for Google Workspace
- **Outlook**: ~300 emails/day
- **Yahoo**: ~500 emails/day

For high-volume newsletters, consider using a dedicated email service provider.
