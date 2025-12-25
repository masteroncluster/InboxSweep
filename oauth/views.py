from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .models import OAuthConnection
from emails.models import EmailAccount

logger = logging.getLogger(__name__)

@login_required
def oauth_connect(request, provider):
    """
    Initiate OAuth connection flow for the specified provider
    """
    # In a real implementation, this would redirect to the provider's OAuth endpoint
    # For now, we'll just show a placeholder page
    context = {
        'provider': provider,
        'provider_name': provider.title(),
    }
    return render(request, 'oauth/connect.html', context)

@login_required
def oauth_callback(request):
    """
    Handle OAuth callback from providers
    """
    # In a real implementation, this would handle the OAuth callback
    # and exchange the authorization code for access tokens
    messages.success(request, "OAuth connection successful!")
    return redirect('oauth_connections')

@login_required
def oauth_connections(request):
    """
    Display user's OAuth connections
    """
    connections = OAuthConnection.objects.filter(user=request.user)
    context = {
        'connections': connections,
    }
    return render(request, 'oauth/connections.html', context)

@login_required
@require_http_methods(["POST"])
def oauth_disconnect(request, connection_id):
    """
    Disconnect an OAuth connection
    """
    try:
        connection = OAuthConnection.objects.get(id=connection_id, user=request.user)
        connection.is_active = False
        connection.save()
        
        # Also deactivate the associated email account
        if connection.email_account:
            connection.email_account.is_active = False
            connection.email_account.save()
        
        messages.success(request, f"Disconnected from {connection.provider.title()}")
    except OAuthConnection.DoesNotExist:
        messages.error(request, "Connection not found")
    
    return redirect('oauth_connections')

@csrf_exempt
@require_http_methods(["POST"])
def oauth_webhook(request, provider):
    """
    Handle webhook notifications from email providers
    """
    try:
        # In a real implementation, this would process webhook notifications
        # from providers like Gmail about new emails, changes, etc.
        data = json.loads(request.body)
        logger.info(f"Received {provider} webhook: {data}")
        
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        logger.error(f"Error processing {provider} webhook: {e}")
        return JsonResponse({'error': str(e)}, status=500)