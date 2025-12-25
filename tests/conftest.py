import pytest
from django.contrib.auth import get_user_model
from emails.models import EmailAccount

User = get_user_model()

@pytest.fixture
def user():
    """Create a test user"""
    return User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123'
    )

@pytest.fixture
def email_account(user):
    """Create a test email account"""
    return EmailAccount.objects.create(
        user=user,
        email_address='test@example.com',
        provider='gmail',
        imap_server='imap.gmail.com',
        smtp_server='smtp.gmail.com',
        password='testpassword'
    )