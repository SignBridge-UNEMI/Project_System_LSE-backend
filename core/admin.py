from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_deaf', 'is_mute', 'is_staff')

admin.site.register(User, UserAdmin)
