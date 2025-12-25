from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import SyncStatus, SyncLog, EmailMessage
from emails.models import EmailAccount
from .services import EmailSyncService
import json

@login_required
def sync_dashboard(request):
    """
    Display synchronization dashboard
    """
    email_accounts = EmailAccount.objects.filter(user=request.user, is_active=True)
    sync_statuses = SyncStatus.objects.filter(email_account__in=email_accounts)
    sync_logs = SyncLog.objects.filter(email_account__in=email_accounts).order_by('-started_at')[:10]
    
    context = {
        'email_accounts': email_accounts,
        'sync_statuses': sync_statuses,
        'sync_logs': sync_logs,
    }
    return render(request, 'sync/dashboard.html', context)

@login_required
@require_http_methods(["POST"])
def start_sync(request, account_id):
    """
    Start synchronization for an email account
    """
    email_account = get_object_or_404(EmailAccount, id=account_id, user=request.user)
    
    try:
        sync_log = EmailSyncService.start_sync(email_account.id, 'full')
        messages.success(request, f"Started synchronization for {email_account.email_address}")
        return JsonResponse({'status': 'success', 'message': 'Sync started'})
    except Exception as e:
        messages.error(request, f"Failed to start synchronization: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def sync_status(request, account_id):
    """
    Get synchronization status for an email account
    """
    email_account = get_object_or_404(EmailAccount, id=account_id, user=request.user)
    sync_status = EmailSyncService.get_sync_status(email_account)
    
    if sync_status:
        return JsonResponse({
            'is_syncing': sync_status.is_syncing,
            'progress': sync_status.progress_percentage,
            'synced_messages': sync_status.synced_messages,
            'total_messages': sync_status.total_messages,
            'last_sync_completed': sync_status.last_sync_completed.isoformat() if sync_status.last_sync_completed else None,
        })
    else:
        return JsonResponse({
            'is_syncing': False,
            'progress': 0,
            'synced_messages': 0,
            'total_messages': 0,
            'last_sync_completed': None,
        })

@login_required
def sync_history(request, account_id):
    """
    Display synchronization history for an email account
    """
    email_account = get_object_or_404(EmailAccount, id=account_id, user=request.user)
    sync_logs = EmailSyncService.get_recent_sync_logs(email_account)
    
    context = {
        'email_account': email_account,
        'sync_logs': sync_logs,
    }
    return render(request, 'sync/history.html', context)

@login_required
def email_list(request, account_id):
    """
    Display list of synchronized emails for an account
    """
    email_account = get_object_or_404(EmailAccount, id=account_id, user=request.user)
    emails = EmailMessage.objects.filter(email_account=email_account).order_by('-received_at')
    
    context = {
        'email_account': email_account,
        'emails': emails,
    }
    return render(request, 'sync/email_list.html', context)

@login_required
def email_detail(request, email_id):
    """
    Display details of a synchronized email
    """
    email = get_object_or_404(EmailMessage, id=email_id, user=request.user)
    
    context = {
        'email': email,
    }
    return render(request, 'sync/email_detail.html', context)