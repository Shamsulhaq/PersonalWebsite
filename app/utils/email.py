"""
Email utility functions for sending emails via SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import os
from datetime import datetime

# Email configuration - can be set via environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", SMTP_USERNAME)
SENDER_NAME = os.getenv("SENDER_NAME", "Personal Site")

def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    plain_content: Optional[str] = None,
    reply_to: Optional[str] = None
) -> bool:
    """
    Send an email via SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML version of email content
        plain_content: Plain text version (optional, will be extracted from HTML if not provided)
        reply_to: Reply-to email address (optional)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("⚠️  Email credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if reply_to:
            msg['Reply-To'] = reply_to
        
        # Add plain text version
        if not plain_content:
            # Simple HTML to text conversion
            import re
            plain_content = re.sub('<[^<]+?>', '', html_content)
        
        part1 = MIMEText(plain_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"✓ Email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to send email to {to_email}: {str(e)}")
        return False

def send_bulk_email(
    recipients: List[str],
    subject: str,
    html_content: str,
    plain_content: Optional[str] = None
) -> dict:
    """
    Send email to multiple recipients
    
    Returns:
        Dictionary with 'success' count and 'failed' list of emails
    """
    results = {'success': 0, 'failed': []}
    
    for email in recipients:
        if send_email(email, subject, html_content, plain_content):
            results['success'] += 1
        else:
            results['failed'].append(email)
    
    return results

def send_contact_reply(
    to_email: str,
    to_name: str,
    original_subject: str,
    reply_message: str,
    sender_name: str,
    sender_email: str
) -> bool:
    """
    Send a reply to a contact form message
    """
    subject = f"Re: {original_subject}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                background: #ffffff;
                padding: 30px;
                border: 1px solid #e2e8f0;
                border-top: none;
            }}
            .message {{
                background: #f8fafc;
                padding: 20px;
                border-left: 4px solid #667eea;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .footer {{
                background: #f8fafc;
                padding: 20px;
                text-align: center;
                font-size: 0.875rem;
                color: #64748b;
                border-radius: 0 0 8px 8px;
                border: 1px solid #e2e8f0;
                border-top: none;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2 style="margin: 0;">Message from {sender_name}</h2>
        </div>
        <div class="content">
            <p>Hi {to_name},</p>
            <p>Thank you for reaching out. Here's my response to your message:</p>
            <div class="message">
                {reply_message.replace(chr(10), '<br>')}
            </div>
            <p>Best regards,<br>{sender_name}</p>
        </div>
        <div class="footer">
            <p>This email was sent in response to your message via {sender_name}'s website contact form.</p>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, html_content, reply_to=sender_email)

def send_newsletter_notification(
    subscribers: List[dict],
    post_title: str,
    post_excerpt: str,
    post_slug: str,
    site_url: str,
    sender_name: str
) -> dict:
    """
    Send new blog post notification to newsletter subscribers
    
    Args:
        subscribers: List of dicts with 'email' and 'name' keys
        post_title: Blog post title
        post_excerpt: Blog post excerpt
        post_slug: Blog post slug for URL
        site_url: Base site URL
        sender_name: Sender name
    
    Returns:
        Dictionary with success count and failed emails
    """
    post_url = f"{site_url}/blog/{post_slug}"
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8fafc;
            }}
            .container {{
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 1.5rem;
            }}
            .content {{
                padding: 30px;
            }}
            .post-title {{
                font-size: 1.5rem;
                color: #1e293b;
                margin: 0 0 15px 0;
                font-weight: 600;
            }}
            .post-excerpt {{
                color: #475569;
                line-height: 1.7;
                margin-bottom: 25px;
            }}
            .btn {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
            }}
            .footer {{
                background: #f8fafc;
                padding: 20px 30px;
                text-align: center;
                font-size: 0.875rem;
                color: #64748b;
            }}
            .footer a {{
                color: #667eea;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📝 New Blog Post from {sender_name}</h1>
            </div>
            <div class="content">
                <p>Hi {subscriber_name},</p>
                <p>A new blog post has just been published!</p>
                <h2 class="post-title">{post_title}</h2>
                <p class="post-excerpt">{post_excerpt}</p>
                <center>
                    <a href="{post_url}" class="btn">Read Full Post →</a>
                </center>
            </div>
            <div class="footer">
                <p>You're receiving this email because you subscribed to {sender_name}'s newsletter.</p>
                <p><a href="{site_url}">Visit Website</a> | <a href="{unsubscribe_url}">Unsubscribe</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    results = {'success': 0, 'failed': []}
    
    for subscriber in subscribers:
        email = subscriber['email']
        name = subscriber.get('name', 'there')
        
        # Personalize content
        html_content = html_template.format(
            sender_name=sender_name,
            subscriber_name=name,
            post_title=post_title,
            post_excerpt=post_excerpt,
            post_url=post_url,
            site_url=site_url,
            unsubscribe_url=f"{site_url}/newsletter/unsubscribe?email={email}"
        )
        
        subject = f"New Post: {post_title}"
        
        if send_email(email, subject, html_content):
            results['success'] += 1
        else:
            results['failed'].append(email)
    
    return results

def test_email_configuration() -> bool:
    """
    Test if email configuration is valid
    """
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        return False
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
        return True
    except Exception as e:
        print(f"Email configuration test failed: {str(e)}")
        return False
