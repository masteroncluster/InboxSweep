from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView, ListView, DetailView
from django.views import View
from django.utils.decorators import method_decorator
from core.mixins import AuthRequiredMixin, AjaxResponseMixin
from .models import SyncStatus, SyncLog, EmailMessage
from emails.models import EmailAccount
from .services import EmailSyncService
import json

class SyncDashboardView(AuthRequiredMixin, TemplateView):
    """Display synchronization dashboard"""
    template_name = 'sync/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        email_accounts = EmailAccount.objects.filter(
            user=self.request.user,
            is_active=True
        )
        sync_statuses = SyncStatus.objects.filter(
            email_account__in=email_accounts
        )
        sync_logs = SyncLog.objects.filter(
            email_account__in=email_accounts
        ).order_by('-started_at')[:10]
        
        context.update({
            'email_accounts': email_accounts,
            'sync_statuses': sync_statuses,
            'sync_logs': sync_logs,
        })
        return context

class StartSyncView(AuthRequiredMixin, AjaxResponseMixin, View):
    """Start synchronization for an email account"""
    
    @method_decorator(require_http_methods(["POST"]))
    def post(self, request, account_id):
        email_account = get_object_or_404(
            EmailAccount,
            id=account_id,
            user=request.user
        )
        
        try:
            sync_log = EmailSyncService.start_sync(email_account.id, 'full')
            messages.success(
                request,
                f"Started synchronization for {email_account.email_address}"
            )
            return self.render_to_json_response({
                'status': 'success',
                'message': 'Sync started'
            })
        except Exception as e:
            messages.error(request, f"Failed to start synchronization: {e}")
            return self.render_to_json_response({
                'status': 'error',
                'message': str(e)
            }, status=500)

class SyncStatusView(AuthRequiredMixin, AjaxResponseMixin, View):
    """Get synchronization status for an email account"""
    
    def get(self, request, account_id):
        email_account = get_object_or_404(
            EmailAccount,
            id=account_id,
            user=request.user
        )
        sync_status = EmailSyncService.get_sync_status(email_account)
        
        if sync_status:
            response_data = {
                'is_syncing': sync_status.is_syncing,
                'progress': sync_status.progress_percentage,
                'synced_messages': sync_status.synced_messages,
                'total_messages': sync_status.total_messages,
                'last_sync_completed': sync_status.last_sync_completed.isoformat()
                    if sync_status.last_sync_completed else None,
            }
        else:
            response_data = {
                'is_syncing': False,
                'progress': 0,
                'synced_messages': 0,
                'total_messages': 0,
                'last_sync_completed': None,
            }
        
        return self.render_to_json_response(response_data)

class SyncHistoryView(AuthRequiredMixin, TemplateView):
    """Display synchronization history for an email account"""
    template_name = 'sync/history.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account_id = kwargs['account_id']
        
        email_account = get_object_or_404(
            EmailAccount,
            id=account_id,
            user=self.request.user
        )
        sync_logs = EmailSyncService.get_recent_sync_logs(email_account)
        
        context.update({
            'email_account': email_account,
            'sync_logs': sync_logs,
        })
        return context

class EmailListView(AuthRequiredMixin, ListView):
    """Display list of synchronized emails for an account"""
    model = EmailMessage
    template_name = 'sync/email_list.html'
    context_object_name = 'emails'
    paginate_by = 50
    
    def get_queryset(self):
        account_id = self.kwargs['account_id']
        return EmailMessage.objects.filter(
            email_account__id=account_id,
            email_account__user=self.request.user
        ).order_by('-received_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email_account'] = get_object_or_404(
            EmailAccount,
            id=self.kwargs['account_id'],
            user=self.request.user
        )
        return context

class EmailDetailView(AuthRequiredMixin, DetailView):
    """Display details of a synchronized email"""
    model = EmailMessage
    template_name = 'sync/email_detail.html'
    context_object_name = 'email'
    
    def get_queryset(self):
        return EmailMessage.objects.filter(
            email_account__user=self.request.user
        )