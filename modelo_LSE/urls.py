from django.urls import path
from .views import predict_sign

urlpatterns = [
    path('predict/', predict_sign, name='predict_sign'),
]