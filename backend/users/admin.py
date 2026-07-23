from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ("id", "username", "email")
    list_filter = ("user_type", "date_joined", "is_superuser", "is_staff", "is_active", "is_verified")
    list_display = ("id", "username", "email", "user_type", "date_joined", "last_login", "is_superuser", "is_staff", "is_active", "is_verified")
