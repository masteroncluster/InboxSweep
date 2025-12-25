# InboxSweep Enhanced Setup Guide

## Prerequisites

Before starting the setup, ensure you have the following installed:
- Python 3.14+
- Docker & Docker Compose
- Git
- Poetry 1.5+
- Code editor (VS Code recommended)

## Step 1: Project Directory Setup

1. Create the project directory:
   ```bash
   mkdir inboxsweep
   cd inboxsweep
   ```

2. Initialize Git repository:
   ```bash
   git init
   ```

3. Create the basic directory structure:
   ```bash
   mkdir -p config accounts oauth sync spam review analytics api core templates static tests
   mkdir -p docs .codeassistant
   ```

## Step 2: Poetry Environment Setup

1. Install Poetry (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Initialize Poetry project:
   ```bash
   poetry init
   ```

3. Create the pyproject.toml file with all dependencies:
   ```toml
   [tool.poetry]
   name = "inboxsweep"
   version = "0.1.0"
   description = "A Django-based email management system for analyzing, categorizing, and cleaning up email inboxes."
   authors = ["InboxSweep Team"]
   license = "Proprietary"
   readme = "README.md"
   packages = [{include = "inboxsweep"}]

   [tool.poetry.dependencies]
   python = "^3.14"
   Django = "^5.0"
   psycopg2-binary = "^2.9.0"
   python-decouple = "^3.8"
   django-allauth = "^0.54.0"
   django-cryptography = "^1.0"
   google-auth = "^2.15.0"
   google-auth-oauthlib = "^1.0.0"
   google-auth-httplib2 = "^0.1.0"
   google-api-python-client = "^2.70.0"
   celery = "^5.3.0"
   redis = "^4.5.0"
   kombu = "^5.3.0"
   imaplib2 = "^3.6.0"
   email-validator = "^1.3.0"
   python-dateutil = "^2.8.0"
   pandas = "^1.5.0"
   numpy = "^1.24.0"
   plotly = "^5.11.0"
   chart.js = "^3.9.0"
   djangorestframework = "^3.14.0"
   django-cors-headers = "^3.13.0"
   drf-spectacular = "^0.26.0"
   gunicorn = "^20.1.0"
   whitenoise = "^6.2.0"
   sentry-sdk = "^1.11.0"
   django-health-check = "^3.17.0"
   django-bootstrap5 = "^22.2"
   django-htmx = "^1.13.0"

   [tool.poetry.group.dev.dependencies]
   pytest = "^7.2.0"
   pytest-django = "^4.5.0"
   pytest-cov = "^4.0.0"
   factory-boy = "^3.2.0"
   black = "^22.10.0"
   flake8 = "^6.0.0"
   isort = "^5.10.0"

   [build-system]
   requires = ["poetry-core"]
   build-backend = "poetry.core.masonry.api"

   [tool.black]
   line-length = 88
   target-version = ['py314']

   [tool.isort]
   profile = "black"
   multi_line_output = 3
   ```

## Step 3: Django Project Creation

1. Create the Django project:
   ```bash
   poetry run django-admin startproject config .
   ```

2. Create the initial apps:
   ```bash
   poetry run python manage.py startapp accounts
   poetry run python manage.py startapp oauth
   poetry run python manage.py startapp sync
   poetry run python manage.py startapp spam
   poetry run python manage.py startapp review
   poetry run python manage.py startapp analytics
   poetry run python manage.py startapp api
   poetry run python manage.py startapp core
   ```

3. Install initial dependencies:
   ```bash
   poetry install
   ```

## Step 4: Environment Configuration

1. Create a `.env.example` file:
   ```env
   # Django Settings
   SECRET_KEY=your-secret-key-here
   DEBUG=1
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database
   DATABASE_URL=postgres://dems_user:dems_password@localhost:5432/dems_dev

   # Redis
   REDIS_URL=redis://localhost:6379/0

   # RabbitMQ
   RABBITMQ_URL=amqp://dems_user:dems_password@localhost:5672/

   # Google OAuth
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/accounts/google/login/callback/

   # Encryption
   ENCRYPTION_KEY=your-encryption-key-here
   ```

2. Create a `.gitignore` file:
   ```gitignore
   # Python
   __pycache__/
   *.py[cod]
   *$py.class
   *.so
   .Python
   build/
   develop-eggs/
   dist/
   downloads/
   eggs/
   .eggs/
   lib/
   lib64/
   parts/
   sdist/
   var/
   wheels/
   *.egg-info/
   .installed.cfg
   *.egg
   .env

   # Django
   *.log
   local_settings.py
   db.sqlite3
   db.sqlite3-journal

   # Virtual Environment
   .venv/
   venv/
   ENV/

   # Poetry
   poetry.lock

   # IDE
   .vscode/
   .idea/
   *.swp
   *.swo

   # Docker
   docker-compose.override.yml
   ```

## Step 5: Docker Configuration

### Dockerfile
Create a `Dockerfile`:
```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
 && poetry install

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Docker Compose Setup
Create the `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: dems_dev
      POSTGRES_USER: dems_user
      POSTGRES_PASSWORD: dems_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7.2
    ports:
      - "6379:6379"

  rabbitmq:
    image: rabbitmq:3.12-management
    environment:
      RABBITMQ_DEFAULT_USER: dems_user
      RABBITMQ_DEFAULT_PASS: dems_password
    ports:
      - "5672:5672"
      - "15672:15672"

  web:
    build: .
    command: poetry run python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
      - DATABASE_URL=postgres://dems_user:dems_password@db:5432/dems_dev
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://dems_user:dems_password@rabbitmq:5672/
    depends_on:
      - db
      - redis
      - rabbitmq

  celery:
    build: .
    command: poetry run celery -A config worker --loglevel=info
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgres://dems_user:dems_password@db:5432/dems_dev
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://dems_user:dems_password@rabbitmq:5672/
    depends_on:
      - db
      - redis
      - rabbitmq

  celery-beat:
    build: .
    command: poetry run celery -A config beat --loglevel=info
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgres://dems_user:dems_password@db:5432/dems_dev
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://dems_user:dems_password@rabbitmq:5672/
    depends_on:
      - db
      - redis
      - rabbitmq

  mailhog:
    image: mailhog/mailhog
    ports:
      - "1025:1025"  # SMTP server
      - "8025:8025"  # Web UI

volumes:
  postgres_data:
```

## Step 6: Development Workflow

### Initial Setup
1. Create a `.env` file with the environment variables:
   ```bash
   cp .env.example .env
   ```

2. Run `docker-compose up --build` to start all services

3. In another terminal, run database migrations:
   ```bash
   docker-compose exec web poetry run python manage.py migrate
   ```

4. Create a superuser:
   ```bash
   docker-compose exec web poetry run python manage.py createsuperuser
   ```

### Development Commands
```bash
# Start all services
docker-compose up

# Run Django shell
docker-compose exec web poetry run python manage.py shell

# Run tests
docker-compose exec web poetry run pytest

# Run specific app tests
docker-compose exec web poetry run pytest emails.tests

# Apply migrations
docker-compose exec web poetry run python manage.py makemigrations
docker-compose exec web poetry run python manage.py migrate

# Create app
docker-compose exec web poetry run python manage.py startapp app_name
```

### Access URLs
- **Application**: http://localhost:8000
- **Admin Interface**: http://localhost:8000/admin
- **Database**: localhost:5432
- **Redis**: localhost:6379
- **RabbitMQ Management**: http://localhost:15672
- **MailHog**: http://localhost:8025

### Stopping Services
1. Use `Ctrl+C` to stop the services
2. Use `docker-compose down` to stop and remove containers
3. Use `docker-compose down -v` to stop and remove volumes

## Step 7: Poetry Commands

```bash
# Install dependencies
poetry install

# Add new dependency
poetry add package_name

# Add development dependency
poetry add --group dev package_name

# Update dependencies
poetry update

# Run command in virtual environment
poetry run python manage.py migrate

# Open virtual environment shell
poetry shell

# Show dependency tree
poetry show --tree

# Check for security vulnerabilities
poetry check
```

## Step 8: Code Quality Setup

### Pre-commit Hooks (Optional)
Install pre-commit hooks:
```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.14

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

Install hooks:
```bash
pre-commit install
```

## Step 9: Testing Setup

### Run Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=. --cov-report=html

# Run specific test file
poetry run pytest emails/tests/test_models.py

# Run in Docker
docker-compose exec web poetry run pytest
```

### Test Configuration
Create `pytest.ini`:
```ini
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.testing"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=. --cov-report=html --cov-report=term"
```

## Step 10: Version Control

1. Add all files to Git:
   ```bash
   git add .
   ```

2. Make the initial commit:
   ```bash
   git commit -m "Initial project setup with Django structure and documentation"
   ```

3. Create the repository on GitHub/GitLab and push:
   ```bash
   git remote add origin <repository-url>
   git push -u origin main
   ```

## Production Considerations

For production deployment, the following changes should be made:

1. Remove MailHog service
2. Use external database instead of containerized PostgreSQL
3. Use external Redis and RabbitMQ instances
4. Add Nginx reverse proxy
5. Add SSL certificate management with Let's Encrypt
6. Configure proper volume mounts for persistent data
7. Set up proper backup and recovery procedures
8. Implement monitoring and alerting

## Troubleshooting

### Common Issues

1. **Permission denied errors**: Ensure proper file permissions on Linux/Mac
2. **Docker daemon not running**: Start Docker service before running docker-compose
3. **Port conflicts**: Change ports in docker-compose.yml if needed
4. **Python version issues**: Ensure Python 3.14+ is installed and used
5. **Poetry installation issues**: Check Poetry documentation for installation troubleshooting

### Getting Help

If you encounter issues:
1. Check the documentation files for guidance
2. Review error messages carefully
3. Search online for Django/Docker/Poetry specific issues
4. Consult the project team for architectural questions

## CI/CD Configuration Guide

### GitHub Actions Configuration

#### Basic Workflow (.github/workflows/ci.yml)

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.14]
        poetry-version: [1.5]

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7.2
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install Poetry
      uses: snok/install-poetry@v1
      with:
        version: ${{ matrix.poetry-version }}
        virtualenvs-create: true
        virtualenvs-in-project: true

    - name: Load cached venv
      id: cached-poetry-dependencies
      uses: actions/cache@v3
      with:
        path: .venv
        key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}

    - name: Install dependencies
      if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
      run: |
        poetry install --no-interaction --no-root

    - name: Install project
      run: |
        poetry install --no-interaction

    - name: Run tests
      run: |
        poetry run pytest
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/postgres
        REDIS_URL: redis://localhost:6379/0

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python 3.14
      uses: actions/setup-python@v4
      with:
        python-version: 3.14

    - name: Install Poetry
      uses: snok/install-poetry@v1
      with:
        version: 1.5
        virtualenvs-create: true
        virtualenvs-in-project: true

    - name: Load cached venv
      id: cached-poetry-dependencies
      uses: actions/cache@v3
      with:
        path: .venv
        key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}

    - name: Install dependencies
      if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
      run: |
        poetry install --no-interaction --no-root

    - name: Install project
      run: |
        poetry install --no-interaction

    - name: Lint with flake8
      run: |
        poetry run flake8 .

    - name: Check formatting with black
      run: |
        poetry run black --check .

    - name: Check imports with isort
      run: |
        poetry run isort --check-only .

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python 3.14
      uses: actions/setup-python@v4
      with:
        python-version: 3.14

    - name: Install Poetry
      uses: snok/install-poetry@v1
      with:
        version: 1.5
        virtualenvs-create: true
        virtualenvs-in-project: true

    - name: Load cached venv
      id: cached-poetry-dependencies
      uses: actions/cache@v3
      with:
        path: .venv
        key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}

    - name: Install dependencies
      if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
      run: |
        poetry install --no-interaction --no-root

    - name: Install project
      run: |
        poetry install --no-interaction

    - name: Run bandit security checks
      run: |
        poetry run bandit -r .

    - name: Check for security vulnerabilities
      run: |
        poetry run safety check
```

### Poetry-Specific CI/CD Best Practices

#### 1. Caching Dependencies

```yaml
# GitHub Actions caching example
- name: Load cached venv
  id: cached-poetry-dependencies
  uses: actions/cache@v3
  with:
    path: .venv
    key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}
```

#### 2. Using Poetry in Scripts

```yaml
# Install dependencies
- name: Install dependencies
  run: |
    poetry install --no-interaction --no-root

# Run tests
- name: Run tests
  run: |
    poetry run pytest

# Run linting
- name: Lint with flake8
  run: |
    poetry run flake8 .
```

#### 3. Environment Variables

```yaml
# Set environment variables for Poetry
env:
  POETRY_VENV_IN_PROJECT: true
  POETRY_CACHE_DIR: /tmp/poetry_cache
```

### Docker Integration with CI/CD

#### Multi-stage Dockerfile

```dockerfile
# Build stage
FROM python:3.14-slim as builder

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
 && poetry install --no-dev --no-interaction --no-ansi

# Production stage
FROM python:3.14-slim as production

WORKDIR /app

# Copy dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /app /app

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
 && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["poetry", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Security Scanning in CI/CD

#### Dependency Vulnerability Scanning

```yaml
security-scan:
  stage: test
  image: python:3.14
  before_script:
    - pip install poetry
    - poetry install
  script:
    - poetry run safety check
    - poetry run bandit -r .
  allow_failure: true
```

## Django 5+ Settings Configuration

### Base Settings (settings/base.py)

```python
"""
Django settings for InboxSweep project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-for-development-only')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition

INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'django.contrib.humanize',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'drf_spectacular',
    'bootstrap5',
    'htmx',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    
    # Project apps
    'accounts',
    'oauth',
    'sync',
    'spam',
    'review',
    'analytics',
    'api',
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'dems_dev'),
        'USER': os.environ.get('DB_USER', 'dems_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'dems_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication settings
AUTH_USER_MODEL = 'accounts.User'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Django Allauth settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'accounts.backends.CaseInsensitiveAuth',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        }
    }
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 1025))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'False').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session settings
SESSION_COOKIE_AGE = 1800  # 30 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF settings
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Django Spectacular settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'InboxSweep API',
    'DESCRIPTION': 'API for the InboxSweep email management system',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Health check settings
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
}

# Custom settings for InboxSweep
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', '')

# Celery settings
CELERY_BROKER_URL = os.environ.get('RABBITMQ_URL', 'amqp://dems_user:dems_password@localhost:5672/')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

### Development Settings (settings/development.py)

```python
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-development-key-only'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable HTTPS in development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Allow CORS in development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'oauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'sync': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'spam': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'review': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'analytics': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Production Settings (settings/production.py)

```python
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Email backend for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Security settings
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 31536000))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True').lower() == 'true'
SECURE_HSTS_PRELOAD = os.environ.get('SECURE_HSTS_PRELOAD', 'True').lower() == 'true'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/inboxsweep.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['file'],
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'oauth': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'sync': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'spam': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'review': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'analytics': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Testing Settings (settings/testing.py)

```python
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-testing-key-only'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Use in-memory database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable HTTPS in testing
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Logging configuration for testing
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

## Next Steps

After completing the initial setup:

1. Configure the Django settings in `config/settings/`
2. Set up the database models in each app
3. Configure URL routing
4. Implement the authentication system
5. Set up the development environment with Docker
6. Begin Phase 1 development (Foundation & Core Authentication)

## Verification Checklist

Before proceeding to development:

- [ ] Django project structure created
- [ ] All required apps initialized
- [ ] Poetry environment set up
- [ ] pyproject.toml file created
- [ ] Docker configuration files created
- [ ] Environment variables configured
- [ ] Git repository initialized
- [ ] Documentation files in place
- [ ] .gitignore configured properly
