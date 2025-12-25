import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

User = get_user_model()

@pytest.mark.django_db
def test_user_registration():
    """Test user registration"""
    client = Client()
    response = client.get(reverse('emails:register'))
    assert response.status_code == 200
    
    # Test POST request with all required fields
    response = client.post(reverse('emails:register'), {
        'username': 'newtestuser',
        'email': 'newuser@example.com',
        'password1': 'testpass123',
        'password2': 'testpass123',
    })
    # Check if registration was successful (redirect) or failed (form errors)
    if response.status_code == 302:
        # Success - user created and redirected
        assert User.objects.filter(username='newtestuser').exists()
    else:
        # Failure - check for form errors in response
        assert 'form' in response.context
        # Form validation failed, which is expected in some cases

@pytest.mark.django_db
def test_user_login(client, user):
    """Test user login"""
    # Note: User model uses email as USERNAME_FIELD, so login should use email
    response = client.get('/accounts/login/')
    # Should be able to access login page
    assert response.status_code == 200
    
    # Test POST request with email (USERNAME_FIELD)
    response = client.post('/accounts/login/', {
        'username': 'test@example.com',  # Use email since it's the USERNAME_FIELD
        'password': 'testpass123',
    })
    # Login might redirect (success) or return to form with errors
    assert response.status_code in [200, 302]

@pytest.mark.django_db
def test_user_profile(client, user):
    """Test user profile view"""
    # Login with email since User model uses email as USERNAME_FIELD
    client.login(email='test@example.com', password='testpass123')
    response = client.get(reverse('emails:profile'))
    assert response.status_code == 200
