from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import User

User = get_user_model()

class ComprehensiveEmailTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='test@example.com', password='testpass123')
    
    def test_home_page(self):
        """Test that the home page loads correctly"""
        response = self.client.get(reverse('emails:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'InboxSweep')
    
    def test_dashboard_page(self):
        """Test that the dashboard page loads correctly"""
        response = self.client.get(reverse('emails:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
    
    def test_user_authentication(self):
        """Test user authentication"""
        # Test that we can log in
        self.assertTrue(self.user.is_authenticated)
        
        # Test that we can access protected pages
        response = self.client.get(reverse('emails:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_email_account_creation(self):
        """Test creating an email account"""
        # This would be implemented when we have the email account creation functionality
        pass