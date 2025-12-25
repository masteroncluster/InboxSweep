from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OAuthConnection
from emails.models import EmailAccount

@receiver(post_save, sender=OAuthConnection)
def update_email_account(sender, instance, created, **kwargs):
    """
    Update or create EmailAccount when OAuthConnection is saved
    """
    if instance.is_active and instance.email_account:
        email_account = instance.email_account
        email_account.oauth_token = instance.access_token
        email_account.is_active = True
        email_account.save()