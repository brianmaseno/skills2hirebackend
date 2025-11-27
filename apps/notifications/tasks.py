"""
Celery tasks for notifications
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def send_verification_email(user_id, token):
    """Send email verification email"""
    try:
        user = User.objects.get(id=user_id)
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        subject = 'Verify your SkillMatchHub account'
        message = f"""
        Hi,
        
        Thank you for registering with SkillMatchHub!
        
        Please verify your email address by clicking the link below:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        The SkillMatchHub Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return f"Verification email sent to {user.email}"
    except User.DoesNotExist:
        return f"User with id {user_id} not found"


@shared_task
def send_password_reset_email(user_id, token):
    """Send password reset email"""
    try:
        user = User.objects.get(id=user_id)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        subject = 'Reset your SkillMatchHub password'
        message = f"""
        Hi,
        
        You requested to reset your password for SkillMatchHub.
        
        Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request a password reset, please ignore this email.
        
        Best regards,
        The SkillMatchHub Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return f"Password reset email sent to {user.email}"
    except User.DoesNotExist:
        return f"User with id {user_id} not found"


@shared_task
def send_application_notification(application_id):
    """Send notification to employer when someone applies to their job"""
    from apps.jobs.models import Application
    
    try:
        application = Application.objects.select_related('job__employer', 'applicant').get(id=application_id)
        employer = application.job.employer
        applicant = application.applicant
        
        subject = f'New application for {application.job.title}'
        message = f"""
        Hi,
        
        {applicant.profile.display_name} ({applicant.email}) has applied to your job posting "{application.job.title}".
        
        Match Score: {application.match_score * 100:.0f}%
        
        Log in to SkillMatchHub to review the application.
        
        Best regards,
        The SkillMatchHub Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [employer.email],
            fail_silently=False,
        )
        
        return f"Application notification sent to {employer.email}"
    except Application.DoesNotExist:
        return f"Application with id {application_id} not found"


@shared_task
def send_message_notification(message_id):
    """Send notification when user receives a new message"""
    from apps.messaging.models import Message
    
    try:
        message = Message.objects.select_related('sender', 'conversation').get(id=message_id)
        conversation = message.conversation
        
        # Send to all participants except sender
        recipients = conversation.participants.exclude(id=message.sender.id)
        
        for recipient in recipients:
            subject = f'New message from {message.sender.profile.display_name}'
            email_message = f"""
            Hi,
            
            You have a new message from {message.sender.profile.display_name}:
            
            "{message.content[:100]}..."
            
            Log in to SkillMatchHub to read and reply.
            
            Best regards,
            The SkillMatchHub Team
            """
            
            send_mail(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient.email],
                fail_silently=False,
            )
        
        return f"Message notifications sent for message {message_id}"
    except Message.DoesNotExist:
        return f"Message with id {message_id} not found"
