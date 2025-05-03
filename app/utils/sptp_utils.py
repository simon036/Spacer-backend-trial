import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app

def send_email(to_email, subject, html_content):
    """
    Send email using SMTP server configured in current_app.config.
    """
    try:
        smtp_server = current_app.config.get('SMTP_SERVER')
        smtp_port = current_app.config.get('SMTP_PORT')
        smtp_username = current_app.config.get('SMTP_USERNAME')
        smtp_password = current_app.config.get('SMTP_PASSWORD')
        smtp_use_tls = current_app.config.get('SMTP_USE_TLS', True)
        from_email = current_app.config.get('SMTP_FROM_EMAIL', 'no-reply@example.com')

        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email

        # Record the MIME types of both parts - text/plain and text/html.
        part = MIMEText(html_content, 'html')
        msg.attach(part)

        # Connect to SMTP server and send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        if smtp_use_tls:
            server.starttls()
        if smtp_username and smtp_password:
            server.login(smtp_username, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        return 250  # SMTP success status code
    except Exception as e:
        print(f"Error sending email via SMTP: {e}")
        return None
