import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from flask import current_app

def configure_sendinblue():
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = current_app.config['SENDINBLUE_API_KEY']
    return sib_api_v3_sdk.ApiClient(configuration)

def send_email(to_email, subject, html_content, sender_name=None, sender_email=None):
    """
    Send email using Sendinblue
    """
    try:
        api_client = configure_sendinblue()
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(api_client)

        sender = {
            "name": sender_name or current_app.config['MAIL_DEFAULT_SENDER_NAME'],
            "email": sender_email or current_app.config['MAIL_DEFAULT_SENDER']
        }

        to = [{"email": to_email}]

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            html_content=html_content,
            sender=sender,
            subject=subject
        )

        result = api_instance.send_transac_email(send_smtp_email)
        return True, result
    except ApiException as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        return False, str(e)

def send_verification_email(email, name, verification_url):
    """
    Send email verification link
    """
    subject = "Verify your Spacer account"
    html_content = f"""
        <p>Hi {name or email},</p>
        <p>Thank you for registering on Spacer platform.</p>
        <p>Please click the following link to verify your email:</p>
        <p><a href="{verification_url}">Verify Email</a></p>
        <p>This link will expire in 24 hours.</p>
    """
    return send_email(email, subject, html_content)

def send_password_reset_email(email, name, reset_url):
    """
    Send password reset link
    """
    subject = "Reset your Spacer password"
    html_content = f"""
        <p>Hi {name or email},</p>
        <p>You requested to reset your password.</p>
        <p>Click the following link to reset your password:</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <p>This link will expire in 1 hour.</p>
    """
    return send_email(email, subject, html_content)

def send_booking_confirmation_email(email, name, booking_details):
    """
    Send booking confirmation email
    """
    subject = "Your Spacer booking confirmation"
    html_content = f"""
        <p>Hi {name or email},</p>
        <p>Your booking has been confirmed!</p>
        <p>Booking details:</p>
        <ul>
            <li>Space: {booking_details['space_name']}</li>
            <li>Date: {booking_details['date']}</li>
            <li>Time: {booking_details['time']}</li>
            <li>Duration: {booking_details['duration']} hours</li>
            <li>Total cost: ${booking_details['total_cost']}</li>
        </ul>
        <p>Thank you for using Spacer!</p>
    """
    return send_email(email, subject, html_content) 