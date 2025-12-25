from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import OAuthConnection

User = get_user_model()

class ComprehensiveOAuthTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='test@example.com', password='testpass123')
    
    def test_oauth_connection_creation(self):
        """Test creating an OAuth connection"""
        connection = OAuthConnection.objects.create(
            user=self.user,
            provider='google',
            access_token='test_access_token',
        )
        
        self.assertEqual(connection.user, self.user)
        self.assertEqual(connection.provider, 'google')
        self.assertEqual(connection.access_token, 'test_access_token')
    
    def test_oauth_connections_page(self):
        """Test that the OAuth connections page loads correctly"""
        response = self.client.get(reverse('oauth:connections'))
        self.assertEqual(response.status_code, 200)
    
    def test_oauth_connect_page(self):
        """Test that the OAuth connect page loads correctly"""
        response = self.client.get(reverse('oauth:connect', kwargs={'provider': 'google'}))
        self.assertEqual(response.status_code, 200)
    
    def test_oauth_disconnect(self):
        """Test disconnecting an OAuth connection"""
        connection = OAuthConnection.objects.create(
            user=self.user,
            provider='google',
            access_token='test_access_token',
        )
        
        response = self.client.post(reverse('oauth:disconnect', kwargs={'connection_id': connection.id}))
        self.assertEqual(response.status_code, 302)  # Redirect after POST
        
        connection.refresh_from_db()
        self.assertFalse(connection.is_active)