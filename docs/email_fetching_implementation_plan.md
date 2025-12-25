# Email Fetching Implementation Plan

## Overview
This plan outlines the implementation of actual email fetching from Gmail API and IMAP providers to complete the InboxSweep email synchronization functionality.

## Current State Analysis
- ✅ OAuth integration working (tests passing)
- ✅ Sync infrastructure complete (models, services, views, URLs, templates)
- ✅ User authentication and account management
- ❌ **Missing**: Actual email fetching from providers

## Implementation Strategy

### Phase 1: Gmail API Integration (2 days)

#### 1.1 Create Gmail Provider Service
**File**: `sync/providers/gmail.py`
```python
class GmailSyncProvider:
    def fetch_emails(self, oauth_connection, from_date=None):
        """Fetch emails from Gmail using OAuth tokens"""
        pass
    
    def parse_gmail_message(self, gmail_message):
        """Parse Gmail API message format to our format"""
        pass
    
    def get_message_details(self, message_id, oauth_connection):
        """Get full message content including body"""
        pass
```

**Key Components**:
- Use Google Gmail API v1
- Leverage existing OAuthConnection for authentication
- Handle pagination for large email sets
- Extract email metadata, body, and attachments
- Convert Gmail format to our EmailMessage model format

#### 1.2 Update EmailSyncService Integration
**File**: `sync/services.py` (add method)
```python
def sync_gmail_account(self, oauth_connection, from_date=None):
    """Sync Gmail account using OAuth connection"""
    pass
```

#### 1.3 Connect Sync Trigger
**File**: `sync/views.py` (StartSyncView.post method)
- Connect start_sync to provider-specific sync
- Add error handling for OAuth failures
- Add progress updates during sync

### Phase 2: IMAP Integration (2 days)

#### 2.1 Create IMAP Provider Service
**File**: `sync/providers/imap.py`
```python
class IMAPSyncProvider:
    def fetch_emails(self, email_account, from_date=None):
        """Fetch emails using IMAP protocol"""
        pass
    
    def parse_imap_message(self, imap_message):
        """Parse IMAP message format to our format"""
        pass
    
    def connect_imap(self, email_account):
        """Establish IMAP connection with credentials"""
        pass
```

**Key Components**:
- Use imaplib2 for IMAP connections
- Support multiple IMAP servers (Gmail IMAP, Outlook, etc.)
- Handle SSL/TLS connections
- Parse MIME email formats
- Extract attachments and metadata

#### 2.2 Connect IMAP Sync
**File**: `sync/services.py` (add method)
```python
def sync_imap_account(self, email_account, from_date=None):
    """Sync IMAP account using stored credentials"""
    pass
```

### Phase 3: Background Tasks (1 day)

#### 3.1 Celery Integration
**File**: `sync/tasks.py`
```python
@shared_task
def sync_email_account_task(email_account_id, sync_type='incremental'):
    """Background task for email synchronization"""
    pass

@shared_task  
def sync_oauth_account_task(oauth_connection_id, sync_type='incremental'):
    """Background task for OAuth account synchronization"""
    pass
```

#### 3.2 Async Sync Triggers
**File**: `sync/views.py`
- Update StartSyncView to trigger background tasks
- Add real-time progress updates via WebSockets or polling

### Phase 4: Email Parsing & Processing (1 day)

#### 4.1 Email Content Processing
**File**: `sync/processors/email_parser.py`
```python
def parse_email_content(raw_email):
    """Parse raw email content to extract components"""
    pass

def extract_attachments(email_message):
    """Extract attachment metadata from email"""
    pass

def sanitize_email_content(content):
    """Sanitize email content for safe display"""
    pass
```

#### 4.2 Attachment Handling
- Store attachment metadata in EmailAttachment model
- Handle large attachments efficiently
- Support various attachment formats

## Implementation Details

### Gmail API Specifics
1. **OAuth Scope**: `https://www.googleapis.com/auth/gmail.readonly`
2. **API Endpoints**:
   - `users.messages.list` - List messages
   - `users.messages.get` - Get message details
   - `users.attachments.get` - Get attachments
3. **Rate Limiting**: Respect Gmail API quotas
4. **Error Handling**: Handle token expiration, API limits

### IMAP Specifics
1. **Connection Handling**:
   - Gmail: `imap.gmail.com:993`
   - Outlook: `outlook.office365.com:993`
   - Yahoo: `imap.mail.yahoo.com:993`
2. **Authentication**: Support both OAuth and password
3. **Folder Mapping**: Map provider folders to labels
4. **Message Format**: Handle various email formats (RFC822, etc.)

### Data Flow
```
User clicks "Start Sync" 
→ StartSyncView triggered
→ EmailSyncService.start_sync() creates sync log
→ Provider-specific sync (Gmail/IMAP)
→ Fetch emails from provider
→ Parse email content
→ Store via EmailSyncService.create_or_update_email_message()
→ Update progress
→ Complete sync log
```

## Testing Strategy

### Unit Tests
- Test Gmail API integration with mock responses
- Test IMAP connection and message parsing
- Test email parsing and metadata extraction
- Test sync service integration

### Integration Tests
- Test complete sync flow with test accounts
- Test OAuth token refresh handling
- Test error handling and recovery
- Test large email set processing

### Performance Tests
- Test sync speed with 1000+ emails
- Test memory usage during large syncs
- Test concurrent sync operations

## Security Considerations

### Credential Security
- Encrypt stored IMAP passwords
- Secure OAuth token storage
- Validate email account ownership

### Content Security
- Sanitize email HTML content
- Validate attachment types and sizes
- Prevent email injection attacks

### API Security
- Implement rate limiting
- Handle API errors gracefully
- Log security events

## Error Handling

### Common Error Scenarios
1. **OAuth Token Expiration**: Refresh tokens automatically
2. **API Rate Limits**: Implement exponential backoff
3. **Network Failures**: Retry with exponential backoff
4. **Invalid Credentials**: Clear error messages
5. **Corrupted Email Data**: Skip and log errors

### Error Recovery
- Resume interrupted syncs
- Partial sync completion handling
- User notification of sync failures

## Success Criteria

### Functional Requirements
- ✅ Gmail accounts can be synchronized via OAuth
- ✅ IMAP accounts can be synchronized via credentials
- ✅ Email metadata is preserved accurately
- ✅ Attachments are captured with metadata
- ✅ Sync progress is tracked and displayed
- ✅ Large email sets can be processed

### Performance Requirements
- ✅ 1000 emails sync in < 5 minutes
- ✅ Memory usage remains stable during large syncs
- ✅ Sync can be paused and resumed
- ✅ Failed syncs can be retried

### User Experience Requirements
- ✅ Clear sync progress indicators
- ✅ Informative error messages
- ✅ Sync history is available
- ✅ Email list loads quickly
- ✅ Sync can be triggered easily

## Timeline Summary

- **Phase 1**: Gmail API Integration (2 days)
- **Phase 2**: IMAP Integration (2 days)  
- **Phase 3**: Background Tasks (1 day)
- **Phase 4**: Email Parsing & Processing (1 day)
- **Testing & Bug Fixes**: (1 day)

**Total Estimated Time**: 7 days

## Dependencies
- Google Gmail API credentials (for Gmail testing)
- Test IMAP account (for IMAP testing)
- Email samples for testing various formats
- OAuth redirect URI configuration

## Next Steps After Implementation
1. Spam detection engine integration
2. Email review and deletion interface
3. Advanced search and filtering
4. Email analytics dashboard
5. Mobile-responsive UI improvements

---

**Note**: This plan assumes existing OAuth integration and sync infrastructure are functional. All implementation should leverage existing EmailSyncService and sync models.
