# InboxSweep Technical Specification

## Project Overview

InboxSweep is a Django-based email management system designed to help users connect their email accounts, analyze email content to identify spam/bulk messages, and safely delete unwanted emails with user confirmation. The system also provides email analytics and user profiling capabilities.

## Technology Stack

### Core Technologies
- **Backend**: Django 5+/Python 3.14
- **Database**: PostgreSQL 14
- **Task Queue**: Celery 5.3 with RabbitMQ 3.12
- **Cache**: Redis 7.2
- **Frontend**: Django Templates + Bootstrap 5 + HTMX
- **Security**: django-cryptography, django-allauth
- **Dependency Management**: Poetry with bleeding-edge dependencies

### Email Integration
- **Gmail**: Google API Python Client with OAuth 2.0
- **IMAP**: Python imaplib with encrypted credential storage
- **OAuth**: django-allauth with custom adapters

### Development & Deployment
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (Production)
- **Application Server**: Gunicorn (Production)
- **SSL**: Let's Encrypt (Production)
- **Monitoring**: Prometheus/Grafana
- **Error Tracking**: Sentry

## System Architecture

```
┌─────────┐    ┌────────────┐    ┌─────────────┐    ┌────────────┐
│  User   │───▶│   Django   │───▶│   Celery    │───▶│  RabbitMQ  │
│ Browser │    │   Views    │    │   Worker    │    │            │
└─────────┘    └────────────┘    └─────────────┘    └────────────┘
                    │                     │                 │
                    ▼                     ▼                 ▼
              ┌────────────┐    ┌─────────────┐    ┌────────────┐
              │ PostgreSQL │    │   Redis     │    │ Email      │
              │            │    │   (Cache)   │    │ Providers  │
              └────────────┘    └─────────────┘    └────────────┘
```

## Development Phases

### Phase 1: Foundation & Core Authentication (4-5 days)
**Goal**: Deployable Django app with user auth and email account model

#### Deliverables:
- Django project setup with `accounts` app
- Poetry dependency management with bleeding-edge dependencies
- Docker setup (Postgres, Redis, RabbitMQ)
- Custom User model with email verification
- EmailAccount model with encryption setup
- Admin interface configuration
- Testing setup with pytest (>80% coverage)

#### Acceptance Criteria:
- ✅ User can register, verify email, log in
- ✅ Admin can manage users/accounts
- ✅ Credentials encrypted at rest
- ✅ Docker compose up launches all services
- ✅ Test suite passes with coverage report

### Phase 2: OAuth Integration & IMAP Client (5-6 days)
**Goal**: Connect to email providers via OAuth and IMAP

#### Deliverables:
- OAuth2 implementation with django-allauth
- Google OAuth with Gmail API scopes
- IMAP client service implementation
- Connection management views
- Folder/Tag synchronization models
- Token refresh mechanism

#### Data Models Added:
```python
class EmailFolder(models.Model):
    account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    full_path = models.CharField(max_length=500)
    folder_type = models.CharField(max_length=50)  # INBOX, SENT, etc.
    unread_count = models.IntegerField(default=0)
    total_count = models.IntegerField(default=0)

class ConnectionLog(models.Model):
    account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # CONNECT, SYNC, ERROR
    status = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
```

#### Acceptance Criteria:
- ✅ Connect Gmail account via OAuth (test with real account)
- ✅ Connect IMAP account (test with test account)
- ✅ List folders/labels from connected account
- ✅ Test connection button works
- ✅ Failed connections logged properly
- ✅ Tokens refresh automatically

### Phase 3: Email Synchronization Engine (6-7 days)
**Goal**: Full email sync with attachments metadata

#### Deliverables:
- EmailMessage and EmailAttachment models
- Sync engine implementation
- Celery tasks for synchronization
- Performance optimizations
- Progress tracking with Redis

#### Data Models:
```python
class EmailMessage(models.Model):
    account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE)
    message_id = models.CharField(max_length=500, db_index=True)
    uid = models.CharField(max_length=255, db_index=True)  # IMAP UID
    thread_id = models.CharField(max_length=255, null=True)
    folder = models.ForeignKey(EmailFolder, on_delete=models.CASCADE)
    
    sender_name = models.CharField(max_length=255)
    sender_email = models.EmailField()
    recipients_to = models.JSONField(default=list)
    recipients_cc = models.JSONField(default=list)
    recipients_bcc = models.JSONField(default=list)
    
    subject = models.TextField()
    body_plain = models.TextField()
    body_html = models.TextField()
    
    received_date = models.DateTimeField()
    sent_date = models.DateTimeField(null=True)
    size_bytes = models.IntegerField()
    
    is_read = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    
    labels = models.JSONField(default=list)
    headers = models.JSONField(default=dict)
    
    synced_at = models.DateTimeField(auto_now=True)

class EmailAttachment(models.Model):
    email = models.ForeignKey(EmailMessage, on_delete=models.CASCADE)
    filename = models.CharField(max_length=500)
    content_type = models.CharField(max_length=255)
    size_bytes = models.IntegerField()
    attachment_id = models.CharField(max_length=500)  # Provider ID
    download_url = models.TextField(blank=True)  # For Gmail API
```

#### Acceptance Criteria:
- ✅ Full sync of 1000+ emails completes in < 5 minutes
- ✅ Incremental sync only fetches new emails
- ✅ All email metadata preserved (headers, labels, flags)
- ✅ Attachments metadata captured
- ✅ Sync can be paused/resumed
- ✅ Memory usage remains stable during large syncs
- ✅ Database indexes optimized for querying

### Phase 4: Spam Detection Engine (5-6 days)
**Goal**: Identify and categorize spam/bulk emails

#### Deliverables:
- SpamRule and SpamAnalysis models
- Rule-based detection strategies
- Statistical bulk detection
- Training interface for user feedback
- Batch processing tasks

#### Data Models:
```python
class SpamRule(models.Model):
    name = models.CharField(max_length=200)
    rule_type = models.CharField(max_length=50, choices=[
        ('sender_pattern', 'Sender Pattern'),
        ('subject_keyword', 'Subject Keyword'),
        ('content_pattern', 'Content Pattern'),
        ('header_analysis', 'Header Analysis'),
    ])
    pattern = models.TextField()
    action = models.CharField(max_length=50, choices=[
        ('mark_spam', 'Mark as Spam'),
        ('categorize', 'Categorize'),
        ('flag_review', 'Flag for Review'),
    ])
    confidence_score = models.FloatField(default=0.7)
    is_active = models.BooleanField(default=True)

class SpamAnalysis(models.Model):
    email = models.OneToOneField(EmailMessage, on_delete=models.CASCADE)
    is_spam = models.BooleanField(default=False)
    confidence = models.FloatField(default=0.0)
    category = models.CharField(max_length=50, choices=[
        ('newsletter', 'Newsletter'),
        ('promotion', 'Promotion'),
        ('social', 'Social'),
        ('transaction', 'Transaction'),
        ('actual_spam', 'Actual Spam'),
        ('bulk', 'Bulk Mail'),
    ])
    matched_rules = models.JSONField(default=list)
    analyzed_at = models.DateTimeField(auto_now=True)
```

#### Acceptance Criteria:
- ✅ Identifies 85%+ of actual spam (test dataset)
- ✅ False positive rate < 5%
- ✅ Categories emails correctly
- ✅ User feedback improves detection
- ✅ Batch processing handles 10k emails/hour
- ✅ Rules can be added/edited via admin

### Phase 5: Email Review & Deletion Interface (4-5 days)
**Goal**: User interface for reviewing and deleting spam

#### Deliverables:
- Review interface with bulk selection
- Deletion workflow models
- Deletion service implementation
- Safety features (undo, trash options)
- Progress tracking UI

#### Data Models:
```python
class DeletionBatch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    
    total_emails = models.IntegerField(default=0)
    total_size = models.BigIntegerField(default=0)
    
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    
    filter_criteria = models.JSONField(default=dict)
    confirmed_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)

class DeletionLog(models.Model):
    batch = models.ForeignKey(DeletionBatch, on_delete=models.CASCADE)
    email = models.ForeignKey(EmailMessage, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    error_message = models.TextField(blank=True)
    deleted_at = models.DateTimeField(null=True)
```

#### Acceptance Criteria:
- ✅ User can filter spam by category/confidence
- ✅ Bulk selection works with 1000+ items
- ✅ Preview shows email content safely
- ✅ Confirmation dialog with summary
- ✅ Deletion progress visible in real-time
- ✅ Undo works within provider limits
- ✅ No accidental deletion of important emails

### Phase 6: Analytics & User Profiling (5-6 days)
**Goal**: Analytics dashboard and digital footprint analysis

#### Deliverables:
- Analytics models for email statistics
- User profile models for digital footprint
- Analytics engine implementation
- Dashboard views with charts
- Scheduled analytics tasks

#### Data Models:
```python
class EmailAnalytics(models.Model):
    account = models.OneToOneField(EmailAccount, on_delete=models.CASCADE)
    period = models.CharField(max_length=20)  # daily, weekly, monthly
    
    total_emails = models.IntegerField(default=0)
    total_spam = models.IntegerField(default=0)
    total_size_mb = models.FloatField(default=0)
    
    top_senders = models.JSONField(default=list)
    top_domains = models.JSONField(default=list)
    category_distribution = models.JSONField(default=dict)
    
    generated_at = models.DateTimeField(auto_now=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Digital Footprint
    known_services = models.JSONField(default=list)
    countries = models.JSONField(default=list)  # From email domains
    languages = models.JSONField(default=list)
    
    # Communication Patterns
    active_hours = models.JSONField(default=dict)
    response_times = models.JSONField(default=dict)
    social_score = models.IntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
```

#### Acceptance Criteria:
- ✅ Dashboard loads in < 3 seconds with 50k emails
- ✅ All charts render correctly with real data
- ✅ Data export contains all filtered data
- ✅ Pattern detection identifies clear trends
- ✅ Service extraction finds > 80% of known services
- ✅ Mobile-responsive dashboard

### Phase 7: Advanced Features & Optimization (6-7 days)
**Goal**: Performance optimization and advanced features

#### Deliverables:
- Database query optimization
- Redis caching layer
- Smart filters and scheduled cleanups
- REST API endpoints
- Monitoring and alerting
- Security hardening

#### Acceptance Criteria:
- ✅ Page load times improved by 40%
- ✅ Memory usage reduced by 30%
- ✅ Database queries optimized (N+1 eliminated)
- ✅ API endpoints documented and functional
- ✅ Monitoring dashboard shows system health
- ✅ Security audit passes with no critical issues

### Phase 8: Production Deployment & Scaling (4-5 days)
**Goal**: Production-ready deployment with scaling

#### Deliverables:
- Docker Compose production configuration
- Nginx reverse proxy configuration
- SSL certificate automation
- CI/CD pipeline setup
- Documentation completion
- Final testing and load testing

#### Acceptance Criteria:
- ✅ Deployed to production server
- ✅ SSL certificate working
- ✅ Backup system tested
- ✅ Load test passes with target metrics
- ✅ Documentation complete
- ✅ Monitoring alerts configured

## Project Structure

```
dems/                          # Django project root
├── config/                    # Django settings and configuration
├── accounts/                 # Phase 1 - User authentication and email accounts
├── oauth/                   # Phase 2 - OAuth integration and IMAP client
├── sync/                    # Phase 3 - Email synchronization engine
├── spam/                    # Phase 4 - Spam detection engine
├── review/                 # Phase 5 - Email review and deletion interface
├── analytics/               # Phase 6 - Analytics and user profiling
├── api/                     # Phase 7 - REST API endpoints
├── core/                    # Shared utilities and common components
├── templates/              # Global templates
├── static/                 # Static assets
├── tests/                   # Global test configurations
├── manage.py               # Django management script
├── pyproject.toml         # Poetry dependencies
├── poetry.lock            # Locked Poetry dependencies
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker image definition
├── .env.example            # Environment variables template
└── README.md               # Project documentation
```

## Success Metrics

| Phase | Key Metric | Target |
|-------|------------|---------|
| 1 | User registration success | > 95% |
| 2 | OAuth connection success | > 90% |
| 3 | Email sync completion | > 99% |
| 4 | Spam detection accuracy | > 85% |
| 5 | Deletion success rate | > 99.9% |
| 6 | Dashboard load time | < 3s |
| 7 | API response time | < 500ms |
| 8 | System uptime | > 99.5% |

## Risk Mitigation

### Phase 1-3: Data Integrity
- Daily automated backups
- Transaction rollback capabilities
- Data validation at all layers

### Phase 4-5: User Trust
- Undo mechanisms
- Preview before deletion
- Confirmation dialogs
- Rate limiting destructive operations

### Phase 6-7: Performance
- Query optimization
- Caching strategy
- Async processing
- Load testing

### Phase 8: Production Stability
- Blue-green deployment
- Rollback procedures
- Monitoring alerts
- Disaster recovery plan

**Total Estimated Development Time**: 40-45 days with parallel development possible after Phase 3.

This phased approach allows multiple AI agents to work concurrently on different phases once dependencies are satisfied, with clear handoff points and integration tests at each stage.
