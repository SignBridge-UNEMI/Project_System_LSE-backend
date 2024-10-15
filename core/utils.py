import secrets
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMessage
from .models import VerificationToken
from django.conf import settings

def generate_verification_token(email):
    """
    Genera un token de verificación único y lo almacena en la base de datos.
    """
    token = secrets.token_urlsafe(32)
    expires = timezone.now() + timedelta(hours=24)  # El token expira en 24 horas

    # Crear un nuevo token de verificación en la base de datos
    VerificationToken.objects.create(
        identifier=email,
        token=token,
        expires=expires
    )

    return token

def send_verification_email(email, token):
    """
    Envía un correo de verificación al usuario con el token generado.
    """
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    email_subject = 'Verify your email'
    email_body = f"Please click the following link to verify your email: {verification_link}"

    email_message = EmailMessage(
        subject=email_subject,
        body=email_body,
        to=[email]
    )
    email_message.send()
