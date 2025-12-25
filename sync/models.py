from django.db import models
from emails.models import User, EmailAccount
from oauth.models import OAuthConnection
from django.utils import timezone

class EmailMessage(models.Model):
    """
    Model to store email message metadata
    """
    # Relationship fields
    email_account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Message identifiers
    message_id = models.CharField(max_length=255, help_text="Provider-specific message ID")
    thread_id = models.CharField(max_length=255, blank=True, help_text="Thread/conversation ID")
    
    # Message metadata
    subject = models.CharField(max_length=500)
    from_address = models.EmailField()
    to_addresses = models.TextField(help_text="JSON list of recipient addresses")
    cc_addresses = models.TextField(blank=True, help_text="JSON list of CC addresses")
    bcc_addresses = models.TextField(blank=True, help_text="JSON list of BCC addresses")
    
    # Content
    snippet = models.TextField(blank=True, help_text="Short preview of message content")
    body_plain = models.TextField(blank=True, help_text="Plain text body")
    body_html = models.TextField(blank=True, help_text="HTML body")
    
    # Dates
    sent_at = models.DateTimeField()
    received_at = models.DateTimeField()
    
    # Flags
    is_read = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    # Categories
    is_spam = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    
    # Size
    size = models.IntegerField(help_text="Message size in bytes")
    
    # Labels/tags
    labels = models.TextField(blank=True, help_text="JSON list of labels/tags")
    
    # Sync metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('email_account', 'message_id')
        indexes = [
            models.Index(fields=['user', 'received_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'is_spam']),
            models.Index(fields=['email_account', 'received_at']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.from_address}"

class EmailAttachment(models.Model):
    """
    Model to store email attachment metadata
    """
    email_message = models.ForeignKey(EmailMessage, on_delete=models.CASCADE, related_name='attachments')
    
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size = models.IntegerField(help_text="Attachment size in bytes")
    attachment_id = models.CharField(max_length=255, help_text="Provider-specific attachment ID")
    
    # In a production environment, we would store the actual attachment content
    # using a storage backend like S3 or Google Cloud Storage
    # For now, we'll just store metadata
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.filename} ({self.content_type})"

class SyncStatus(models.Model):
    """
    Model to track synchronization status for email accounts
    """
    email_account = models.OneToOneField(EmailAccount, on_delete=models.CASCADE)
    
    # Sync status
    is_syncing = models.BooleanField(default=False)
    last_sync_started = models.DateTimeField(null=True, blank=True)
    last_sync_completed = models.DateTimeField(null=True, blank=True)
    last_sync_error = models.TextField(blank=True)
    
    # Progress tracking
    total_messages = models.IntegerField(default=0)
    synced_messages = models.IntegerField(default=0)
    
    # Sync settings
    sync_from_date = models.DateTimeField(null=True, blank=True, help_text="Sync messages from this date")
    sync_to_date = models.DateTimeField(null=True, blank=True, help_text="Sync messages up to this date")
    
    # Provider-specific info
    provider_folder = models.CharField(max_length=255, blank=True, help_text="Folder/label being synced")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Sync status for {self.email_account}"
    
    @property
    def progress_percentage(self):
        """Calculate sync progress percentage"""
        if self.total_messages > 0:
            return min(100, int((self.synced_messages / self.total_messages) * 100))
        return 0
    
    @property
    def is_complete(self):
        """Check if sync is complete"""
        return self.total_messages > 0 and self.synced_messages >= self.total_messages

class SyncLog(models.Model):
    """
    Model to log synchronization events
    """
    SYNC_TYPES = [
        ('full', 'Full Sync'),
        ('incremental', 'Incremental Sync'),
        ('folder', 'Folder Sync'),
    ]
    
    SYNC_STATUSES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    email_account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE)
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES)
    status = models.CharField(max_length=20, choices=SYNC_STATUSES)
    
    # Stats
    messages_processed = models.IntegerField(default=0)
    messages_added = models.IntegerField(default=0)
    messages_updated = models.IntegerField(default=0)
    messages_deleted = models.IntegerField(default=0)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    
    # Timing
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['email_account', '-started_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Sync log for {self.email_account} - {self.sync_type} ({self.status})"