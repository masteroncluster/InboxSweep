from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import EmailMessage, EmailAttachment, SyncStatus, SyncLog
from emails.models import EmailAccount
import json

User = get_user_model()

class ComprehensiveSyncTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.email_account = EmailAccount.objects.create(
            user=self.user,
            email_address='test@example.com',
            provider='google',
            imap_server='imap.gmail.com',
            smtp_server='smtp.gmail.com',
        )
        self.client.login(username='test@example.com', password='testpass123')
    
    def test_sync_dashboard_page(self):
        """Test that the sync dashboard page loads correctly"""
        response = self.client.get(reverse('sync:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_email_message_creation(self):
        """Test creating an email message"""
        message = EmailMessage.objects.create(
            email_account=self.email_account,
            user=self.user,
            message_id='12345',
            subject='Test Email',
            from_address='sender@example.com',
            to_addresses=json.dumps(['recipient@example.com']),
            sent_at='2025-12-25T10:00:00Z',
            received_at='2025-12-25T10:05:00Z',
            size=1024,
        )
        
        self.assertEqual(message.subject, 'Test Email')
        self.assertEqual(message.from_address, 'sender@example.com')
    
    def test_email_attachment_creation(self):
        """Test creating an email attachment"""
        message = EmailMessage.objects.create(
            email_account=self.email_account,
            user=self.user,
            message_id='12345',
            subject='Test Email',
            from_address='sender@example.com',
            to_addresses=json.dumps(['recipient@example.com']),
            sent_at='2025-12-25T10:00:00Z',
            received_at='2025-12-25T10:05:00Z',
            size=1024,
        )
        
        attachment = EmailAttachment.objects.create(
            email_message=message,
            filename='test.pdf',
            content_type='application/pdf',
            size=2048,
            attachment_id='attach123',
        )
        
        self.assertEqual(attachment.filename, 'test.pdf')
        self.assertEqual(attachment.content_type, 'application/pdf')
    
    def test_sync_status_creation(self):
        """Test creating a sync status"""
        sync_status = SyncStatus.objects.create(
            email_account=self.email_account,
            is_syncing=True,
            total_messages=100,
            synced_messages=50,
        )
        
        self.assertEqual(sync_status.progress_percentage, 50)
        self.assertFalse(sync_status.is_complete)
    
    def test_sync_log_creation(self):
        """Test creating a sync log"""
        from django.utils import timezone
        sync_log = SyncLog.objects.create(
            email_account=self.email_account,
            sync_type='full',
            status='completed',
            messages_processed=100,
            started_at=timezone.now(),
        )
        
        self.assertEqual(sync_log.messages_processed, 100)
        self.assertEqual(sync_log.status, 'completed')
    
    def test_email_list_page(self):
        """Test that the email list page loads correctly"""
        response = self.client.get(reverse('sync:email_list', kwargs={'account_id': self.email_account.id}))
        self.assertEqual(response.status_code, 200)
    
    def test_sync_history_page(self):
        """Test that the sync history page loads correctly"""
        response = self.client.get(reverse('sync:sync_history', kwargs={'account_id': self.email_account.id}))
        self.assertEqual(response.status_code, 200)