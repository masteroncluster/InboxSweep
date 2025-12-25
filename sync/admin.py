from django.contrib import admin
from .models import EmailMessage, EmailAttachment, SyncStatus, SyncLog

@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'from_address', 'received_at', 'email_account', 'is_read', 'is_spam')
    list_filter = ('is_read', 'is_spam', 'is_important', 'received_at', 'email_account')
    search_fields = ('subject', 'from_address', 'to_addresses')
    readonly_fields = ('created_at', 'updated_at', 'last_synced_at')
    
    fieldsets = (
        ('Message Info', {
            'fields': ('email_account', 'user', 'message_id', 'thread_id', 'subject', 
                      'from_address', 'to_addresses', 'cc_addresses', 'bcc_addresses')
        }),
        ('Content', {
            'fields': ('snippet', 'body_plain', 'body_html'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('sent_at', 'received_at')
        }),
        ('Flags', {
            'fields': ('is_read', 'is_starred', 'is_draft', 'is_deleted', 'is_spam', 'is_important')
        }),
        ('Metadata', {
            'fields': ('size', 'labels', 'created_at', 'updated_at', 'last_synced_at')
        }),
    )

@admin.register(EmailAttachment)
class EmailAttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'content_type', 'size', 'email_message')
    list_filter = ('content_type',)
    search_fields = ('filename',)
    readonly_fields = ('created_at',)

@admin.register(SyncStatus)
class SyncStatusAdmin(admin.ModelAdmin):
    list_display = ('email_account', 'is_syncing', 'progress_percentage', 'last_sync_completed')
    list_filter = ('is_syncing',)
    readonly_fields = ('updated_at', 'progress_percentage')

@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ('email_account', 'sync_type', 'status', 'messages_processed', 'started_at')
    list_filter = ('sync_type', 'status', 'started_at')
    readonly_fields = ('created_at', 'completed_at')
    
    fieldsets = (
        ('Sync Info', {
            'fields': ('email_account', 'sync_type', 'status')
        }),
        ('Stats', {
            'fields': ('messages_processed', 'messages_added', 'messages_updated', 'messages_deleted')
        }),
        ('Error Info', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'created_at')
        }),
    )