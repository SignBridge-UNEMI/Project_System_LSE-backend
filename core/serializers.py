from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)  # Asegúrate de que sea write_only

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "password",
            "confirm_password",
            "is_deaf",
            "is_mute",
            "security_question_1",
            "security_answer_1",
            "security_question_2",
            "security_answer_2",
        ]

    def validate_email(self, value):
        """Verifica que el email sea único."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está en uso.")
        return value

    def validate_password(self, value):
        """Asegura que la contraseña cumpla con ciertos criterios."""
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        # Puedes agregar más reglas aquí si lo deseas (ej: mayúsculas, números, etc.)
        return value

    def validate(self, validated_data):
        """Validar los datos de entrada."""
        if validated_data['password'] != validated_data['confirm_password']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})

        if not validated_data.get('security_answer_1'):
            raise serializers.ValidationError({"security_answer_1": "La respuesta a la pregunta de seguridad 1 es requerida."})
        if not validated_data.get('security_answer_2'):
            raise serializers.ValidationError({"security_answer_2": "La respuesta a la pregunta de seguridad 2 es requerida."})

        return validated_data

    def create(self, validated_data):
        """Crear un nuevo usuario con los datos validados."""
        validated_data.pop("confirm_password")
        
        user = User(
            email=validated_data["email"],
            name=validated_data.get("name", ""),
            is_deaf=validated_data.get("is_deaf", False),
            is_mute=validated_data.get("is_mute", False),
            security_question_1=validated_data.get("security_question_1", ""),
            security_question_2=validated_data.get("security_question_2", ""),
        )

        user.set_security_answer_1(validated_data.get("security_answer_1", ""))
        user.set_security_answer_2(validated_data.get("security_answer_2", ""))
        
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserReadSerializer(serializers.ModelSerializer):
    """Serializador para la lectura del usuario (excluye campos sensibles)."""
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "is_deaf",
            "is_mute",
        ]


class LoginSerializer(serializers.Serializer):
    """Serializador para el inicio de sesión."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validar las credenciales del usuario durante el inicio de sesión."""
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(request=self.context.get("request"), username=email, password=password)

        if user is None:
            raise serializers.ValidationError("Credenciales inválidas.")

        if not user.email_verified:
            raise serializers.ValidationError("El correo no ha sido verificado. Por favor revisa tu bandeja de entrada.")

        attrs["user"] = user  # Almacenar el usuario autenticado
        return attrs
