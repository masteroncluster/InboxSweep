from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import OAuthConnection
from emails.models import EmailAccount
from .services import OAuthService

User = get_user_model()

class OAuthModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_oauth_connection_creation(self):
        """Test creating an OAuth connection"""
        connection = OAuthConnection.objects.create(
            user=self.user,
            provider='google',
            access_token='test_access_token',
            refresh_token='test_refresh_token',
            token_expiry=timezone.now() + timedelta(hours=1),
            scopes='["https://www.googleapis.com/auth/gmail.readonly"]'
        )
        
        self.assertEqual(str(connection), "test@example.com - google OAuth")
        self.assertFalse(connection.is_expired())
    
    def test_oauth_connection_expiration(self):
        """Test OAuth connection expiration"""
        connection = OAuthConnection.objects.create(
            user=self.user,
            provider='google',
            access_token='test_access_token',
            token_expiry=timezone.now() - timedelta(hours=1),  # Expired
        )
        
        self.assertTrue(connection.is_expired())

class OAuthServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_or_update_connection(self):
        """Test creating or updating an OAuth connection"""
        connection = OAuthService.create_or_update_connection(
            user=self.user,
            provider='google',
            access_token='test_access_token',
            refresh_token='test_refresh_token',
            expires_in=3600,
            scopes=['https://www.googleapis.com/auth/gmail.readonly'],
            email_address='test@example.com'
        )
        
        self.assertEqual(connection.user, self.user)
        self.assertEqual(connection.provider, 'google')
        self.assertEqual(connection.access_token, 'test_access_token')
        self.assertEqual(connection.refresh_token, 'test_refresh_token')
        
        # Test updating existing connection
        updated_connection = OAuthService.create_or_update_connection(
            user=self.user,
            provider='google',
            access_token='new_access_token',
            refresh_token='new_refresh_token',
            expires_in=7200,
            scopes=['https://www.googleapis.com/auth/gmail.readonly', 
                   'https://www.googleapis.com/auth/gmail.send'],
            email_address='test@example.com'
        )
        
        self.assertEqual(updated_connection.id, connection.id)
        self.assertEqual(updated_connection.access_token, 'new_access_token')
        self.assertEqual(updated_connection.refresh_token, 'new_refresh_token')
    
    def test_get_active_connections(self):
        """Test getting active OAuth connections"""
        # Create active connection
        OAuthConnection.objects.create(
            user=self.user,
            provider='google',
            access_token='test_token',
            is_active=True
        )
        
        # Create inactive connection
        OAuthConnection.objects.create(
            user=self.user,
            provider='microsoft',
            access_token='test_token',
            is_active=False
        )
        
        active_connections = OAuthService.get_active_connections(self.user)
        self.assertEqual(active_connections.count(), 1)
        self.assertEqual(active_connections.first().provider, 'google')
    
    def test_deactivate_connection(self):
        """Test deactivating an OAuth connection"""
        connection = OAuthConnection.objects.create(
            user=self.user,
            provider='google',
            access_token='test_token',
            is_active=True
        )
        
        result = OAuthService.deactivate_connection(connection.id, self.user)
        self.assertTrue(result)
        
        connection.refresh_from_db()
        self.assertFalse(connection.is_active)