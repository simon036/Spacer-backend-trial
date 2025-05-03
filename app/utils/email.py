from flask import current_app
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from typing import List, Optional

def send_email(
    to_email: str,
    subject: str,
    content: str,
    html_content: Optional[str] = None,
    from_email: Optional[str] = None
) -> bool:
    """
    Send an email using Sendinblue (Brevo).
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        content (str): Plain text content
        html_content (str, optional): HTML content. If not provided, plain text will be used
        from_email (str, optional): Sender email. If not provided, default sender will be used
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Configure API key
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = current_app.config['SENDINBLUE_API_KEY']
        
        # Create an instance of the API class
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        # Set up sender
        sender = {"email": from_email or current_app.config['MAIL_DEFAULT_SENDER'],
                 "name": current_app.config.get('MAIL_DEFAULT_SENDER_NAME', 'Spacer')}
        
        # Set up recipient
        to = [{"email": to_email}]
        
        # Create email object
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            sender=sender,
            subject=subject,
            text_content=content,
            html_content=html_content or content
        )
        
        # Send email
        api_response = api_instance.send_transac_email(send_smtp_email)
        return True
    except ApiException as e:
        current_app.logger.error(f"Failed to send email via Sendinblue: {str(e)}")
        return False
    except Exception as e:
        current_app.logger.error(f"Unexpected error while sending email: {str(e)}")
        return False

def send_verification_email(user_email: str, token: str) -> bool:
    """
    Send a verification email to a user.
    
    Args:
        user_email (str): User's email address
        token (str): Verification token
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    verification_url = f"{current_app.config['FRONTEND_URL']}/verify-email?token={token}"
    
    subject = "Verify your Spacer account"
    html_content = f"""
    <h2>Welcome to Spacer!</h2>
    <p>Please click the link below to verify your email address:</p>
    <p><a href="{verification_url}">Verify Email</a></p>
    <p>If you didn't create an account with us, you can safely ignore this email.</p>
    <p>This link will expire in 24 hours.</p>
    """
    
    return send_email(user_email, subject, "", html_content=html_content)

def send_password_reset_email(user_email: str, token: str) -> bool:
    """
    Send a password reset email to a user.
    
    Args:
        user_email (str): User's email address
        token (str): Password reset token
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={token}"
    
    subject = "Reset your Spacer password"
    html_content = f"""
    <h2>Password Reset Request</h2>
    <p>You recently requested to reset your password. Click the link below to reset it:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>If you didn't request a password reset, you can safely ignore this email.</p>
    <p>This link will expire in 1 hour.</p>
    """
    
    return send_email(user_email, subject, "", html_content=html_content)

def send_booking_confirmation_email(
    user_email: str,
    space_name: str,
    start_date: str,
    end_date: str,
    total_price: float
) -> bool:
    """
    Send a booking confirmation email.
    
    Args:
        user_email (str): User's email address
        space_name (str): Name of the booked space
        start_date (str): Booking start date
        end_date (str): Booking end date
        total_price (float): Total booking price
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = f"Booking Confirmation - {space_name}"
    html_content = f"""
    <h2>Booking Confirmation</h2>
    <p>Your booking for {space_name} has been confirmed!</p>
    <h3>Booking Details:</h3>
    <ul>
        <li>Space: {space_name}</li>
        <li>Start Date: {start_date}</li>
        <li>End Date: {end_date}</li>
        <li>Total Price: ${total_price:.2f}</li>
    </ul>
    <p>Thank you for choosing Spacer!</p>
    """
    
    return send_email(user_email, subject, "", html_content=html_content) 