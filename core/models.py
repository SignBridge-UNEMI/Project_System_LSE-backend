from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)  # Asegúrate de que el email sea único
    name = models.CharField(max_length=255, blank=True)
    is_deaf = models.BooleanField(default=False)
    is_mute = models.BooleanField(default=False)

    # Campos de preguntas de seguridad
    security_question_1 = models.CharField(max_length=255, blank=True)
    security_answer_1 = models.CharField(max_length=255, blank=True)
    security_question_2 = models.CharField(max_length=255, blank=True)
    security_answer_2 = models.CharField(max_length=255, blank=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email')
        ]

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)
