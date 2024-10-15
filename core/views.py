from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.db import transaction  # Para el manejo de transacciones
from django.utils import timezone  # Para manejar la fecha y hora
from .models import User, VerificationToken
from .serializers import UserSerializer


class RegisterView(generics.CreateAPIView):
    """
    Vista para el registro de nuevos usuarios.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        with transaction.atomic():  # Asegura que todas las operaciones sean atómicas
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Aquí podrías enviar un correo de verificación al usuario
            VerificationToken.create_for_user(user)

            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "refresh": str(refresh),  # Token de refresh JWT
                "access": str(access_token),  # Token de acceso JWT
                "message": "Usuario registrado correctamente. Por favor, verifica tu correo.",
            }, status=status.HTTP_201_CREATED)


class LoginSerializer(serializers.Serializer):
    """
    Serializador para el inicio de sesión de usuarios.
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Autenticación del usuario utilizando el email como username
        user = authenticate(request=self.context.get('request'), username=email, password=password)

        if user is None:
            raise serializers.ValidationError("Credenciales incorrectas.")

        # Verificar si el usuario ha verificado su correo
        if not user.email_verified:
            raise serializers.ValidationError("Debes verificar tu correo electrónico antes de iniciar sesión.")

        attrs['user'] = user
        return attrs


class LoginView(generics.GenericAPIView):
    """
    Vista para el inicio de sesión de usuarios.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Autenticación del usuario
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Crear respuesta
            response = Response({
                'access': str(access_token),  # Incluir access_token en el cuerpo
                'refresh': str(refresh),      # Incluir refresh_token en el cuerpo
                'message': 'Inicio de sesión exitoso'
            })

            # Establecer las cookies
            response.set_cookie(
                key='accessToken', value=str(access_token), httponly=True, samesite='None', secure=True
            )
            response.set_cookie(
                key='refreshToken', value=str(refresh), httponly=True, samesite='None', secure=True
            )

            return response
        except APIException as api_exception:
            return Response({'error': str(api_exception)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Ocurrió un error interno: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyEmailView(generics.GenericAPIView):
    """
    Vista para verificar el correo electrónico utilizando un token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")

        # Verificar si existe un token en la base de datos
        verify_token = VerificationToken.objects.filter(token=token).first()
        if not verify_token:
            return Response({"message": "Token no encontrado."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si el token ya expiró
        if verify_token.is_expired():
            return Response({"message": "Token expirado."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si el token ya fue utilizado
        if verify_token.is_used:
            return Response({"message": "El token ya ha sido utilizado."}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar al usuario asociado con el token
        user = User.objects.filter(email=verify_token.identifier).first()
        if user is None:
            return Response({"message": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Verificar si el email ya está verificado
        if user.email_verified:
            return Response({"message": "Email ya verificado."}, status=status.HTTP_400_BAD_REQUEST)

        # Marcar el email como verificado
        user.email_verified = True  # Cambia a True para indicar que el email está verificado
        user.save()

        # Marcar el token como utilizado
        verify_token.is_used = True
        verify_token.used_at = timezone.now()  # Registrar cuándo se utilizó el token
        verify_token.save()

        return Response({"message": "Email verificado con éxito."}, status=status.HTTP_200_OK)

