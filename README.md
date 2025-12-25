# InboxSweep

A Django-based email management system for analyzing, categorizing, and cleaning up email inboxes.

## Project Overview

InboxSweep helps users:
- Connect their email accounts (Gmail via OAuth, IMAP/SMTP)
- Analyze email content to identify spam/bulk messages
- Safely delete unwanted emails with user confirmation
- Gain insights through email analytics and user profiling

## Key Features

- **Email Authentication & Connection**: OAuth 2.0 integration with Google, IMAP/SMTP support
- **Email Synchronization**: Full email sync with metadata preservation
- **Spam Detection**: Rule-based and statistical spam/bulk email detection
- **Email Management**: Bulk selection interface with safe deletion workflows
- **Analytics Dashboard**: Email statistics and user profiling
- **Encrypted Storage**: Secure credential storage with django-cryptography

## Technology Stack

- **Backend**: Django 5+/Python 3.14, PostgreSQL 14
- **Task Processing**: Celery 5.3 with RabbitMQ 3.12
- **Caching**: Redis 7.2
- **Frontend**: Django Templates + Bootstrap 5 + HTMX
- **Security**: django-cryptography, django-allauth
- **Dependency Management**: Poetry with bleeding-edge dependencies

## Development Phases

The project is structured into 8 sequential phases, each with clear deliverables:

1. **Foundation & Core Authentication** (4-5 days)
2. **OAuth Integration & IMAP Client** (5-6 days)
3. **Email Synchronization Engine** (6-7 days)
4. **Spam Detection Engine** (5-6 days)
5. **Email Review & Deletion Interface** (4-5 days)
6. **Analytics & User Profiling** (5-6 days)
7. **Advanced Features & Optimization** (6-7 days)
8. **Production Deployment & Scaling** (4-5 days)

## Documentation

- [Technical Specification](docs/inboxsweep_plan.md) - Detailed technical specification
- [Technical Documentation](docs/inboxsweep_tech_doc.md) - Core technical documentation
- [Architecture Plan](docs/inboxsweep_architecture_plan.md) - System architecture and design
- [Implementation Guide](docs/next_steps_implementation_guide.md) - Development approach and next steps
- [Project Requirements](docs/project_requirements.md) - Dependencies and system requirements
- [Docker Setup](docs/docker_compose_setup.md) - Docker configuration guide
- [Initial Setup Guide](docs/initial_setup_guide.md) - Project initialization steps
- [Poetry Migration Guide](docs/poetry_migration_guide.md) - Poetry migration instructions
- [Project Summary](docs/inboxsweep_project_summary.md) - Comprehensive project overview

## Getting Started

1. Review the [Initial Setup Guide](docs/initial_setup_guide.md) for project initialization steps
2. Set up the development environment using the [Docker Setup Guide](docs/docker_compose_setup.md)
3. Follow the [Implementation Guide](docs/next_steps_implementation_guide.md) to begin development

## Project Structure

```
inboxsweep/
├── config/                 # Django settings and configuration
├── accounts/              # User authentication and email accounts
├── oauth/                 # OAuth integration and IMAP client
├── sync/                  # Email synchronization engine
├── spam/                  # Spam detection engine
├── review/                # Email review and deletion interface
├── analytics/            # Analytics and user profiling
├── api/                   # REST API endpoints
├── core/                  # Shared utilities and common components
├── templates/             # Global templates
├── static/               # Static assets
├── tests/                # Global test configurations
├── docs/                 # Project documentation
├── .codeassistant/       # MCP configuration
├── .venv/                # Python virtual environment
├── manage.py            # Django management script
├── pyproject.toml       # Poetry dependencies
├── poetry.lock          # Locked Poetry dependencies
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile          # Docker image definition
├── .env.example        # Environment variables template
└── .gitignore          # Git ignore rules
```

## Development Approach

This project follows a phased development approach optimized for AI agent development:
- Each phase has isolated models/features
- Minimal inter-phase dependencies
- Clear acceptance criteria per phase
- All phases independently testable

## Success Metrics

- Email sync completion > 99%
- Spam detection accuracy > 85%
- Deletion success rate > 99.9%
- Dashboard load time < 3s
- API response time < 500ms
- System uptime > 99.5%

## Contributing

1. Follow the setup instructions in the [Initial Setup Guide](docs/initial_setup_guide.md)
2. Review the [Architecture Plan](docs/inboxsweep_architecture_plan.md) before making changes
3. Ensure all tests pass before submitting pull requests
4. Follow the coding standards outlined in the documentation

## License

This project is proprietary and confidential. All rights reserved.

## Contact

For questions about this project, please refer to the documentation or contact the development team.