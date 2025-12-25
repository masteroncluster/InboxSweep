from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmailAccount

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'email_verified', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'email_verified')
    search_fields = ('email', 'username')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Email Verification', {'fields': ('email_verified', 'email_verified_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

@admin.register(EmailAccount)
class EmailAccountAdmin(admin.ModelAdmin):
    list_display = ('email_address', 'user', 'provider', 'is_active', 'created_at')
    list_filter = ('provider', 'is_active', 'created_at')
    search_fields = ('email_address', 'user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
