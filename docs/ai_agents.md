# Django Developer Guidelines

**Primary Objective:** Write clean, tested Django code. KISS principle - working code over documentation.

## Core Rules
- **Framework:** Django 5.0+
- **Views:** Class-Based Views (CBV) preferred over Function-Based Views (FBV)
- **Testing:** `pytest` preferred, `unittest` acceptable
- **Database:** Django ORM only, avoid raw SQL
- **Dependencies:** Poetry with bleeding-edge versions

## ❌ Avoid At All Costs
- Documentation files unless explicitly required
- Architecture documents over coding
- Over-architecting (microservices when monolith works)
- Function-Based Views beyond simple health checks
- Raw SQL when ORM suffices
- OAuth tokens in plain text

## ✅ Preferred Patterns

### Class-Based Views
```python
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    
    def get_object(self):
        return self.request.user

class EmailListView(LoginRequiredMixin, ListView):
    model = EmailMessage
    paginate_by = 50
    
    def get_queryset(self):
        return EmailMessage.objects.filter(
            account__user=self.request.user
        ).order_by('-received_at')
```

### Models
```python
class EmailAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_address = models.EmailField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

@property
def is_connected(self):
    return self.oauth_connections.filter(is_active=True).exists()
```

### Security
```python
from django_cryptography.fields import EncryptedTextField

class OAuthConnection(models.Model):
    access_token = EncryptedTextField()
    refresh_token = EncryptedTextField(blank=True)
    expires_at = models.DateTimeField()
```

## Testing Workflow (Mandatory)
```bash
# After EVERY change:
python manage.py test app.tests
pytest -xvs
pytest --cov=. --cov-report=html

# Requirements:
✓ All tests pass
✓ New code >80% coverage
✓ No regressions
✓ PEP8 compliance
```

## Documentation Policy
**Write only when:**
1. API endpoints created/updated (update OpenAPI/Swagger)
2. Complex business logic needs docstrings
3. Environment setup changes (update README.md)

**Never create:**
- Design documents
- Implementation diaries
- Architecture decision records

## Task Execution
1. **Code first:** Implement core functionality immediately
2. **Test concurrently:** Write tests while coding
3. **Verify immediately:** Run tests after each change
4. **Refactor based on results**

## Development Workflow
```bash
# Before committing:
black . --check
flake8 .
pytest --cov=. --cov-report=html
```

## API Development (Django REST Framework)
```python
from rest_framework import viewsets, permissions

class EmailAccountViewSet(viewsets.ModelViewSet):
    serializer_class = EmailAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return EmailAccount.objects.filter(user=self.request.user)
```

## Celery Tasks
```python
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def sync_email_account(self, account_id):
    try:
        account = EmailAccount.objects.get(id=account_id)
        sync_service = EmailSyncService(account)
        sync_service.full_sync()
    except Exception as exc:
        self.retry(countdown=60, exc=exc)
```

## Performance
```python
# Database optimization
def get_queryset(self):
    return EmailMessage.objects.select_related(
        'email_account__user'
    ).prefetch_related('attachments')

# Database indexes
class Meta:
    indexes = [
        models.Index(fields=['email_account', '-received_at']),
        models.Index(fields=['sender_email', 'is_read']),
    ]
```

## Error Handling
```python
import logging
logger = logging.getLogger(__name__)

def sync_emails(account):
    try:
        logger.info(f"Started sync for account {account.id}")
        # sync logic
    except Exception as e:
        logger.error(f"Sync failed for account {account.id}: {e}")
        raise
```

## Final Checklist
- [ ] Code uses CBV where appropriate
- [ ] Sensitive data encrypted
- [ ] Database queries optimized
- [ ] Tests pass with >80% coverage
- [ ] Security best practices followed
- [ ] PEP8 standards met
- [ ] No unnecessary documentation

**Success metric:** Working, tested Django code in repository - not documentation created.
