from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import hashlib

class User(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser.
    Incluye campos adicionales como email, nombre, y respuestas de seguridad.
    """
    email = models.EmailField(unique=True)  # Asegúrate de que el email sea único
    name = models.CharField(max_length=255, blank=True)  # Nombre del usuario
    is_deaf = models.BooleanField(default=False)  # Indica si el usuario es sordo
    is_mute = models.BooleanField(default=False)  # Indica si el usuario es mudo

    # Campos de preguntas de seguridad
    security_question_1 = models.CharField(max_length=255, blank=True)  # Primera pregunta de seguridad
    security_answer_1 = models.CharField(max_length=255, blank=True)  # Respuesta a la primera pregunta de seguridad
    security_question_2 = models.CharField(max_length=255, blank=True)  # Segunda pregunta de seguridad
    security_answer_2 = models.CharField(max_length=255, blank=True)  # Respuesta a la segunda pregunta de seguridad

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",
        blank=True,
        help_text="Los grupos a los que pertenece este usuario. Un usuario obtendrá todos los permisos otorgados a cada uno de sus grupos.",
        verbose_name="grupos",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions_set",
        blank=True,
        help_text="Permisos específicos para este usuario.",
        verbose_name="permisos de usuario",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email')  # Asegura que no haya emails duplicados
        ]

    def save(self, *args, **kwargs):
        """
        Sobrescribir el método save para establecer el nombre de usuario como el email si no se ha proporcionado.
        """
        if not self.username:
            self.username = self.email  # Establecer el username como el email
        super().save(*args, **kwargs)  # Llamar al método save de la clase base

    def set_security_answer_1(self, answer):
        """
        Cifrar la respuesta a la primera pregunta de seguridad.
        """
        self.security_answer_1 = hashlib.sha256(answer.encode()).hexdigest()

    def set_security_answer_2(self, answer):
        """
        Cifrar la respuesta a la segunda pregunta de seguridad.
        """
        self.security_answer_2 = hashlib.sha256(answer.encode()).hexdigest()


class VerificationToken(models.Model):
    """
    Modelo para los tokens de verificación de email.
    Se utiliza para almacenar el token, su estado, y su fecha de expiración.
    """
    identifier = models.EmailField()  # Almacena el email del usuario asociado al token
    token = models.CharField(max_length=255, unique=True)  # Token único para la verificación
    expires = models.DateTimeField()  # Fecha y hora de expiración del token
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha y hora de creación del token
    is_used = models.BooleanField(default=False)  # Indica si el token ya ha sido utilizado
    used_at = models.DateTimeField(null=True, blank=True)  # Registra cuándo se utilizó el token

    def is_expired(self):
        """
        Verifica si el token ha expirado.
        """
        return timezone.now() > self.expires

    def __str__(self):
        """
        Representación en cadena del modelo VerificationToken.
        """
        return f"VerificationToken(identifier={self.identifier}, token={self.token}, expires={self.expires})"
