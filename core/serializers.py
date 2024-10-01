from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction

# Serializador para el registro de usuarios
class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)

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

    def validate(self, validated_data):
        """
        Validar los datos de entrada.
        - Verifica que las contraseñas coincidan.
        - Verifica que las respuestas de seguridad no estén vacías.
        """
        # Verificar que las contraseñas coincidan
        if validated_data['password'] != validated_data['confirm_password']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})

        # Validar respuestas de seguridad
        if not validated_data.get('security_answer_1'):
            raise serializers.ValidationError({"security_answer_1": "La respuesta a la pregunta de seguridad 1 es requerida."})
        if not validated_data.get('security_answer_2'):
            raise serializers.ValidationError({"security_answer_2": "La respuesta a la pregunta de seguridad 2 es requerida."})

        return validated_data

    def create(self, validated_data):
        """
        Crear un nuevo usuario con los datos validados.
        """
        # Remover confirm_password antes de crear el usuario
        validated_data.pop("confirm_password")
        
        # Crear una instancia del usuario
        user = User(
            email=validated_data["email"],
            name=validated_data.get("name", ""),
            is_deaf=validated_data.get("is_deaf", False),
            is_mute=validated_data.get("is_mute", False),
            security_question_1=validated_data.get("security_question_1", ""),
            security_answer_1=validated_data.get("security_answer_1", ""),
            security_question_2=validated_data.get("security_question_2", ""),
            security_answer_2=validated_data.get("security_answer_2", ""),
        )
        
        # Establecer la contraseña usando el método adecuado
        user.set_password(validated_data["password"])
        user.save()
        return user


# Serializador para la lectura del usuario (excluye campos sensibles)
class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "is_deaf",
            "is_mute",
        ]


# Serializador para el inicio de sesión
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        Validar las credenciales del usuario durante el inicio de sesión.
        """
        email = attrs.get("email")
        password = attrs.get("password")

        # Autenticación del usuario utilizando el campo 'email'
        user = authenticate(
            request=self.context.get("request"), username=email, password=password
        )

        if user is None:
            raise serializers.ValidationError("Credenciales inválidas")

        attrs["user"] = user  # Almacenar el usuario autenticado
        return attrs