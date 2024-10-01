from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import VerificationToken

@receiver(post_save, sender=VerificationToken)
def mark_token_as_used(sender, instance, created, **kwargs):
    """Marca el token como usado y registra el tiempo de uso."""
    if not created and instance.is_used:
        instance.used_at = timezone.now()
        instance.save()
