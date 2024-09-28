from django.urls import path
from core import views

urlpatterns = [
    path('api/hello/', views.hello, name='hello'),
]