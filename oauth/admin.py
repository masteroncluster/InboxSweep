from django.contrib import admin
from .models import OAuthConnection

@admin.register(OAuthConnection)
class OAuthConnectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'is_active', 'created_at', 'token_expiry')
    list_filter = ('provider', 'is_active', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at', 'last_sync')
    
    fieldsets = (
        ('Connection Info', {
            'fields': ('user', 'email_account', 'provider', 'is_active')
        }),
        ('Token Information', {
            'fields': ('access_token', 'refresh_token', 'token_expiry', 'scopes'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'last_sync')
        }),
    )