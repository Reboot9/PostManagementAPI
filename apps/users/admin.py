from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.forms import CustomUserCreationForm, CustomUserChangeForm
from apps.users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin class for CustomUser model.
    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ["is_active", "is_staff", "is_superuser"]
    list_editable = [
        "is_active",
    ]
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ("Timestamps", {"fields": ("last_login", "created_at", "updated_at"),
                        "classes": ("collapse",), }, ),
    )

    # fields displayed on User creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active')}
         ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    readonly_fields = ("created_at", "updated_at")
