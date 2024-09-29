from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

# Registro
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
        # Verificar que las contraseñas coincidan
        if validated_data['password'] != validated_data['confirm_password']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return validated_data

    def create(self, validated_data):
        validated_data.pop("confirm_password")  # Remover confirm_password antes de crear el usuario
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
        user.set_password(validated_data["password"])  # Asegúrate de usar este método
        user.save()
        return user


# Login
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # Aquí se usa el campo 'email' para autenticar
        user = authenticate(
            request=self.context.get("request"), username=email, password=password
        )

        if user is None:
            raise serializers.ValidationError("Credenciales inválidas")

        attrs["user"] = user
        return attrs
