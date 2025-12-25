from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import EmailAccount

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """Test that user is created correctly"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertFalse(self.user.email_verified)
    
    def test_user_email_verification(self):
        """Test that user email verification works"""
        self.user.verify_email()
        self.assertTrue(self.user.email_verified)
        self.assertIsNotNone(self.user.email_verified_at)

class EmailAccountModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.email_account = EmailAccount.objects.create(
            user=self.user,
            email_address='test@example.com',
            provider='Gmail',
            imap_server='imap.gmail.com',
            smtp_server='smtp.gmail.com',
            password='testpassword'
        )
    
    def test_email_account_creation(self):
        """Test that email account is created correctly"""
        self.assertEqual(self.email_account.email_address, 'test@example.com')
        self.assertEqual(self.email_account.provider, 'Gmail')
        self.assertEqual(self.email_account.user, self.user)
        self.assertTrue(self.email_account.is_active)
    
    def test_email_account_string_representation(self):
        """Test that email account string representation is correct"""
        self.assertEqual(str(self.email_account), 'test@example.com (Gmail)')
