# OptifluenceLMS - Loan Management System

A comprehensive loan management system built with Django 5.0 and Supabase, designed to streamline loan processing, customer management, and financial tracking.

## Project Structure

```
optifluenceLMS/
├── apps/                    # Django applications
│   ├── accounts/           # User authentication and profiles
│   ├── customers/          # Customer management
│   ├── loans/              # Loan products and applications
│   └── transactions/       # Financial transactions and repayments
├── config/                 # Project configuration
│   ├── settings/          # Environment-specific settings
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI configuration
├── docs/                   # Project documentation
│   ├── erd.drawio         # Entity Relationship Diagram
│   └── database.sql       # Database schema
├── static/                # Static files (CSS, JS, Images)
│   ├── css/              # Stylesheets
│   └── images/           # Static images
├── media/                 # User-uploaded files
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   └── includes/         # Reusable template parts
├── .env                   # Environment variables (not in git)
├── .env.example          # Example environment configuration
├── .gitignore            # Git ignore rules
├── LICENSE               # Project license
├── README.md             # Project documentation
├── manage.py             # Django management script
└── requirements.txt      # Python dependencies

```

## Features

- User Authentication and Authorization
- Customer Management
- Loan Product Configuration
- Loan Application Processing
- Document Management
- Transaction Tracking
- Repayment Scheduling
- Email Notifications

## Technology Stack

- Python 3.12
- Django 5.0
- Supabase (PostgreSQL)
- Django REST Framework
- Simple JWT Authentication
- MailerSend (Email Service)
- Celery (Task Queue)
- Redis (Message Broker)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/optifluenceLMS.git
   cd optifluenceLMS
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv312
   source venv312/bin/activate  # On Windows: venv312\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run development server:
   ```bash
   python manage.py runserver
   ```

## Environment Variables

See `.env.example` for required environment variables.

## Development

1. Create new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes and commit:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

3. Push changes:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create pull request on GitHub

## Testing

Run tests with:
```bash
python manage.py test
```

## License

This project is licensed under the terms of the license included in the repository.

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request

## Security

Report security issues to [security contact]

## Support

For support, email [support contact]