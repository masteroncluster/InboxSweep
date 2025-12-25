from django.db import models
from emails.models import User, EmailAccount
from django.utils import timezone
import json

class OAuthConnection(models.Model):
    """
    Model to store OAuth connection details and tokens
    """
    PROVIDER_CHOICES = [
        ('google', 'Google/Gmail'),
        ('microsoft', 'Microsoft/Outlook'),
        ('yahoo', 'Yahoo Mail'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_account = models.OneToOneField(EmailAccount, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    scopes = models.TextField(help_text="JSON list of granted scopes")
    
    # Connection metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'provider')
    
    def __str__(self):
        return f"{self.user.email} - {self.provider} OAuth"
    
    def is_expired(self):
        """Check if the access token has expired"""
        if not self.token_expiry:
            return True
        return timezone.now() >= self.token_expiry
    
    def get_scopes(self):
        """Get scopes as a list"""
        if self.scopes:
            return json.loads(self.scopes)
        return []
    
    def set_scopes(self, scopes_list):
        """Set scopes from a list"""
        self.scopes = json.dumps(scopes_list)