from django.contrib import admin
from .models import UserProfile

# Register your models here.
admin.site.register(UserProfile)
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'role')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')

admin.site.register(CustomUser, CustomUserAdmin)
