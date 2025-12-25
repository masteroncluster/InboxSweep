from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from django.views.generic import TemplateView, ListView, DeleteView
from django.views import View
from django.utils.decorators import method_decorator
from core.mixins import AuthRequiredMixin, AjaxResponseMixin, CsrfExemptMixin
from .models import OAuthConnection
from emails.models import EmailAccount

logger = logging.getLogger(__name__)

class OAuthConnectView(AuthRequiredMixin, TemplateView):
    """Initiate OAuth connection flow for the specified provider"""
    template_name = 'oauth/connect.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        provider = kwargs.get('provider')
        context.update({
            'provider': provider,
            'provider_name': provider.title(),
        })
        return context

class OAuthCallbackView(AuthRequiredMixin, View):
    """Handle OAuth callback from providers"""
    
    def get(self, request):
        # In a real implementation, this would handle the OAuth callback
        # and exchange the authorization code for access tokens
        messages.success(request, "OAuth connection successful!")
        return redirect('oauth:connections')

class OAuthConnectionsView(AuthRequiredMixin, ListView):
    """Display user's OAuth connections"""
    template_name = 'oauth/connections.html'
    context_object_name = 'connections'
    
    def get_queryset(self):
        return OAuthConnection.objects.filter(user=self.request.user)

class OAuthDisconnectView(AuthRequiredMixin, View):
    """Disconnect an OAuth connection"""
    
    def post(self, request, connection_id):
        connection = get_object_or_404(
            OAuthConnection,
            id=connection_id,
            user=request.user
        )
        
        # Deactivate the connection
        connection.is_active = False
        connection.save()
        
        # Also deactivate the associated email account
        if connection.email_account:
            connection.email_account.is_active = False
            connection.email_account.save()
        
        messages.success(
            request,
            f"Disconnected from {connection.provider.title()}"
        )
        return redirect('oauth:connections')

class OAuthWebhookView(CsrfExemptMixin, AjaxResponseMixin, View):
    """Handle webhook notifications from email providers"""
    
    @method_decorator(require_http_methods(["POST"]))
    def post(self, request, provider):
        try:
            # In a real implementation, this would process webhook notifications
            # from providers like Gmail about new emails, changes, etc.
            data = json.loads(request.body)
            logger.info(f"Received {provider} webhook: {data}")
            
            return self.render_to_json_response({'status': 'ok'})
        except Exception as e:
            logger.error(f"Error processing {provider} webhook: {e}")
            return self.render_to_json_response(
                {'error': str(e)},
                status=500
            )