from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.db import transaction  # Importar para manejo de transacciones
from .models import User
from .serializers import UserSerializer, LoginSerializer

class RegisterView(generics.CreateAPIView):
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


class LoginView(generics.GenericAPIView):
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
