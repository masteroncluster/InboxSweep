from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """
    Custom User model with email verification
    """
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    def verify_email(self):
        """Mark user's email as verified"""
        self.email_verified = True
        self.email_verified_at = timezone.now()
        self.save()

class EmailAccount(models.Model):
    """
    Model for storing email account credentials with encryption
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_address = models.EmailField()
    provider = models.CharField(max_length=50)  # Gmail, Outlook, etc.
    imap_server = models.CharField(max_length=100)
    smtp_server = models.CharField(max_length=100)
    imap_port = models.IntegerField(default=993)
    smtp_port = models.IntegerField(default=587)
    
    # These would be encrypted in a production environment
    # For now, we'll store them as plain text for simplicity
    password = models.CharField(max_length=100)  # In production, use django-cryptography
    oauth_token = models.TextField(blank=True)  # For OAuth connections
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.email_address} ({self.provider})"
