from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import EmailMessage, EmailAttachment, SyncStatus, SyncLog
from emails.models import EmailAccount
from .services import EmailSyncService
import json

User = get_user_model()

class SyncModelTest(TestCase):
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
    
    def test_email_message_creation(self):
        """Test creating an email message"""
        message = EmailMessage.objects.create(
            email_account=self.email_account,
            user=self.user,
            message_id='12345',
            subject='Test Email',
            from_address='sender@example.com',
            to_addresses=json.dumps(['recipient@example.com']),
            sent_at=timezone.now(),
            received_at=timezone.now(),
            size=1024,
        )
        
        self.assertEqual(str(message), "Test Email - sender@example.com")
    
    def test_email_attachment_creation(self):
        """Test creating an email attachment"""
        message = EmailMessage.objects.create(
            email_account=self.email_account,
            user=self.user,
            message_id='12345',
            subject='Test Email',
            from_address='sender@example.com',
            to_addresses=json.dumps(['recipient@example.com']),
            sent_at=timezone.now(),
            received_at=timezone.now(),
            size=1024,
        )
        
        attachment = EmailAttachment.objects.create(
            email_message=message,
            filename='test.pdf',
            content_type='application/pdf',
            size=2048,
            attachment_id='attach123',
        )
        
        self.assertEqual(str(attachment), "test.pdf (application/pdf)")
    
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
        sync_log = SyncLog.objects.create(
            email_account=self.email_account,
            sync_type='full',
            status='completed',
            messages_processed=100,
            started_at=timezone.now(),
            completed_at=timezone.now() + timedelta(minutes=5),
        )
        
        self.assertEqual(str(sync_log), f"Sync log for {self.email_account} - full (completed)")

class SyncServiceTest(TestCase):
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
    
    def test_start_sync(self):
        """Test starting a sync"""
        sync_log = EmailSyncService.start_sync(self.email_account.id, 'full')
        
        self.assertEqual(sync_log.email_account, self.email_account)
        self.assertEqual(sync_log.sync_type, 'full')
        self.assertEqual(sync_log.status, 'started')
        
        # Check that sync status was created
        sync_status = EmailSyncService.get_sync_status(self.email_account)
        self.assertIsNotNone(sync_status)
        self.assertTrue(sync_status.is_syncing)
    
    def test_update_sync_progress(self):
        """Test updating sync progress"""
        sync_log = EmailSyncService.start_sync(self.email_account.id, 'full')
        EmailSyncService.update_sync_progress(sync_log, processed=10, added=8, updated=2)
        
        sync_log.refresh_from_db()
        self.assertEqual(sync_log.messages_processed, 10)
        self.assertEqual(sync_log.messages_added, 8)
        self.assertEqual(sync_log.messages_updated, 2)
    
    def test_complete_sync(self):
        """Test completing a sync"""
        sync_log = EmailSyncService.start_sync(self.email_account.id, 'full')
        EmailSyncService.complete_sync(sync_log)
        
        sync_log.refresh_from_db()
        self.assertEqual(sync_log.status, 'completed')
        self.assertIsNotNone(sync_log.completed_at)
        
        # Check that sync status was updated
        sync_status = EmailSyncService.get_sync_status(self.email_account)
        self.assertFalse(sync_status.is_syncing)
        self.assertIsNotNone(sync_status.last_sync_completed)
    
    def test_create_or_update_email_message(self):
        """Test creating or updating an email message"""
        message_data = {
            'id': 'msg123',
            'subject': 'Test Email',
            'from': 'sender@example.com',
            'to': ['recipient@example.com'],
            'received_at': timezone.now(),
            'size': 1024,
        }
        
        email_message, created = EmailSyncService.create_or_update_email_message(
            self.email_account, message_data
        )
        
        self.assertTrue(created)
        self.assertEqual(email_message.subject, 'Test Email')
        self.assertEqual(email_message.from_address, 'sender@example.com')