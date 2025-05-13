from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'role')
    search_fields = ("roll_number","name")
# Register your models here.
admin.site.register(UserProfile,UserProfileAdmin)
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'role')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')

admin.site.register(CustomUser, CustomUserAdmin)
