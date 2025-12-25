import logging
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from .models import EmailMessage, EmailAttachment, SyncStatus, SyncLog
from emails.models import EmailAccount
from oauth.models import OAuthConnection

logger = logging.getLogger(__name__)

class EmailSyncService:
    """
    Service class for handling email synchronization
    """
    
    @staticmethod
    def start_sync(email_account_id, sync_type='full'):
        """
        Start synchronization for an email account
        """
        try:
            email_account = EmailAccount.objects.get(id=email_account_id)
            
            # Create or update sync status
            sync_status, created = SyncStatus.objects.get_or_create(
                email_account=email_account,
                defaults={
                    'is_syncing': True,
                    'last_sync_started': timezone.now(),
                }
            )
            
            if not created:
                sync_status.is_syncing = True
                sync_status.last_sync_started = timezone.now()
                sync_status.save()
            
            # Create sync log
            sync_log = SyncLog.objects.create(
                email_account=email_account,
                sync_type=sync_type,
                status='started',
                started_at=timezone.now(),
            )
            
            logger.info(f"Started {sync_type} sync for {email_account}")
            return sync_log
            
        except EmailAccount.DoesNotExist:
            logger.error(f"Email account {email_account_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error starting sync for account {email_account_id}: {e}")
            raise
    
    @staticmethod
    def update_sync_progress(sync_log, processed=0, added=0, updated=0, deleted=0):
        """
        Update sync progress
        """
        sync_log.messages_processed += processed
        sync_log.messages_added += added
        sync_log.messages_updated += updated
        sync_log.messages_deleted += deleted
        sync_log.status = 'in_progress'
        sync_log.save()
        
        # Update sync status if we have an email account
        if sync_log.email_account:
            try:
                sync_status = SyncStatus.objects.get(email_account=sync_log.email_account)
                sync_status.synced_messages = sync_log.messages_processed
                sync_status.save()
            except SyncStatus.DoesNotExist:
                pass
    
    @staticmethod
    def complete_sync(sync_log, error_message=None):
        """
        Complete synchronization
        """
        sync_log.completed_at = timezone.now()
        
        if error_message:
            sync_log.status = 'failed'
            sync_log.error_message = error_message
        else:
            sync_log.status = 'completed'
        
        sync_log.save()
        
        # Update sync status
        if sync_log.email_account:
            try:
                sync_status = SyncStatus.objects.get(email_account=sync_log.email_account)
                sync_status.is_syncing = False
                sync_status.last_sync_completed = timezone.now()
                if error_message:
                    sync_status.last_sync_error = error_message
                sync_status.save()
            except SyncStatus.DoesNotExist:
                pass
        
        logger.info(f"Completed sync for {sync_log.email_account} with status: {sync_log.status}")
    
    @staticmethod
    def create_or_update_email_message(email_account, message_data):
        """
        Create or update an email message
        """
        try:
            with transaction.atomic():
                # Convert addresses to JSON strings
                to_addresses = json.dumps(message_data.get('to', []))
                cc_addresses = json.dumps(message_data.get('cc', []))
                bcc_addresses = json.dumps(message_data.get('bcc', []))
                labels = json.dumps(message_data.get('labels', []))
                
                # Create or update the email message
                email_message, created = EmailMessage.objects.update_or_create(
                    email_account=email_account,
                    message_id=message_data['id'],
                    defaults={
                        'user': email_account.user,
                        'thread_id': message_data.get('thread_id', ''),
                        'subject': message_data.get('subject', ''),
                        'from_address': message_data.get('from', ''),
                        'to_addresses': to_addresses,
                        'cc_addresses': cc_addresses,
                        'bcc_addresses': bcc_addresses,
                        'snippet': message_data.get('snippet', ''),
                        'body_plain': message_data.get('body_plain', ''),
                        'body_html': message_data.get('body_html', ''),
                        'sent_at': message_data.get('sent_at', timezone.now()),
                        'received_at': message_data.get('received_at', timezone.now()),
                        'is_read': message_data.get('is_read', False),
                        'is_starred': message_data.get('is_starred', False),
                        'is_draft': message_data.get('is_draft', False),
                        'is_deleted': message_data.get('is_deleted', False),
                        'is_spam': message_data.get('is_spam', False),
                        'is_important': message_data.get('is_important', False),
                        'size': message_data.get('size', 0),
                        'labels': labels,
                        'last_synced_at': timezone.now(),
                    }
                )
                
                # Handle attachments
                if 'attachments' in message_data:
                    for attachment_data in message_data['attachments']:
                        EmailAttachment.objects.update_or_create(
                            email_message=email_message,
                            attachment_id=attachment_data['id'],
                            defaults={
                                'filename': attachment_data.get('filename', ''),
                                'content_type': attachment_data.get('content_type', ''),
                                'size': attachment_data.get('size', 0),
                            }
                        )
                
                return email_message, created
                
        except Exception as e:
            logger.error(f"Error creating/updating email message: {e}")
            raise
    
    @staticmethod
    def get_sync_status(email_account):
        """
        Get synchronization status for an email account
        """
        try:
            return SyncStatus.objects.get(email_account=email_account)
        except SyncStatus.DoesNotExist:
            return None
    
    @staticmethod
    def get_recent_sync_logs(email_account, limit=10):
        """
        Get recent sync logs for an email account
        """
        return SyncLog.objects.filter(email_account=email_account).order_by('-started_at')[:limit]
    
    @staticmethod
    def get_email_count_by_account(user):
        """
        Get email count by account for a user
        """
        return EmailMessage.objects.filter(user=user).values(
            'email_account__email_address'
        ).annotate(
            count=models.Count('id')
        ).order_by('-count')

# Provider-specific sync services would be implemented here
# For example: GmailSyncService, OutlookSyncService, etc.