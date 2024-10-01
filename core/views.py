from rest_framework import generics, status, serializers
from rest_framework.response import Response
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

            # Establecer el username como el email
            user.username = user.email
            
            # Establecer las respuestas de seguridad (cifradas)
            user.set_security_answer_1(request.data.get('security_answer_1'))
            user.set_security_answer_2(request.data.get('security_answer_2'))
            
            # Guardar el usuario en la base de datos
            user.save()

            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "refresh": str(refresh),  # Token de refresh JWT
                "access": str(access_token),  # Token de acceso JWT
                "message": "Usuario registrado correctamente.",
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

        # Autenticación del usuario
        user = authenticate(request=self.context.get('request'), email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Credenciales incorrectas.")
        
        attrs['user'] = user
        return attrs


class LoginView(generics.GenericAPIView):
    """
    Vista para el inicio de sesión de usuarios.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]  # Permitir acceso sin necesidad de autenticación

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Autenticación del usuario
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),  # Token de refresh JWT
            'access': str(refresh.access_token),  # Token de acceso JWT
            'message': 'Inicio de sesión exitoso'
        })


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
        if verify_token.expires < timezone.now():
            return Response({"message": "Token expirado."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si el email ya está verificado
        user = User.objects.filter(email=verify_token.identifier).first()
        if user and user.email_verified:
            return Response({"message": "Email ya verificado."}, status=status.HTTP_400_BAD_REQUEST)

        # Marcar el email como verificado
        user.email_verified = timezone.now()
        user.save()

        # Eliminar el token
        verify_token.delete()

        return Response({"message": "Email verificado con éxito."}, status=status.HTTP_200_OK)
