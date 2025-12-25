import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from .models import OAuthConnection
from emails.models import EmailAccount

logger = logging.getLogger(__name__)

class OAuthService:
    """
    Service class for handling OAuth operations
    """
    
    @staticmethod
    def create_or_update_connection(user, provider, access_token, refresh_token=None, 
                                 expires_in=None, scopes=None, email_address=None):
        """
        Create or update an OAuth connection for a user
        """
        try:
            # Get or create the OAuth connection
            connection, created = OAuthConnection.objects.get_or_create(
                user=user,
                provider=provider,
                defaults={
                    'access_token': access_token,
                    'refresh_token': refresh_token or '',
                    'is_active': True,
                }
            )
            
            # Update the connection details
            connection.access_token = access_token
            if refresh_token:
                connection.refresh_token = refresh_token
            if expires_in:
                connection.token_expiry = timezone.now() + timedelta(seconds=expires_in)
            if scopes:
                connection.set_scopes(scopes)
            connection.is_active = True
            connection.save()
            
            # Create or update the email account
            if email_address:
                email_account, _ = EmailAccount.objects.get_or_create(
                    user=user,
                    email_address=email_address,
                    defaults={
                        'provider': provider,
                        'is_active': True,
                        'oauth_token': access_token,
                    }
                )
                # Update the email account
                email_account.provider = provider
                email_account.oauth_token = access_token
                email_account.is_active = True
                email_account.save()
                
                # Link the connection to the email account
                connection.email_account = email_account
                connection.save()
            
            logger.info(f"OAuth connection {'created' if created else 'updated'} for {user.email} with {provider}")
            return connection
            
        except Exception as e:
            logger.error(f"Error creating/updating OAuth connection: {e}")
            raise
    
    @staticmethod
    def refresh_access_token(connection):
        """
        Refresh the access token for an OAuth connection
        """
        # In a real implementation, this would make an API call to refresh the token
        # For now, we'll just log the action
        logger.info(f"Refreshing access token for {connection.user.email} - {connection.provider}")
        # This is where you would implement the actual token refresh logic
        # using the refresh_token and provider-specific APIs
        pass
    
    @staticmethod
    def is_token_expired(connection):
        """
        Check if the OAuth token is expired
        """
        if not connection.token_expiry:
            return False
        return timezone.now() >= connection.token_expiry
    
    @staticmethod
    def get_active_connections(user):
        """
        Get all active OAuth connections for a user
        """
        return OAuthConnection.objects.filter(user=user, is_active=True)
    
    @staticmethod
    def deactivate_connection(connection_id, user):
        """
        Deactivate an OAuth connection
        """
        try:
            connection = OAuthConnection.objects.get(id=connection_id, user=user)
            connection.is_active = False
            connection.save()
            
            # Also deactivate the associated email account
            if connection.email_account:
                connection.email_account.is_active = False
                connection.email_account.save()
            
            logger.info(f"Deactivated OAuth connection {connection_id} for {user.email}")
            return True
        except OAuthConnection.DoesNotExist:
            logger.warning(f"OAuth connection {connection_id} not found for {user.email}")
            return False