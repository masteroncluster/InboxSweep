from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from oauth.models import OAuthConnection

User = get_user_model()

def home(request):
    """
    Home page view
    """
    context = {
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'emails/home.html', context)

@login_required
def dashboard(request):
    """
    User dashboard view
    """
    connections = OAuthConnection.objects.filter(user=request.user)
    
    context = {
        'connections': connections,
        'connection_count': connections.count(),
    }
    return render(request, 'emails/dashboard.html', context)
