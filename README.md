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
│   ├── database/          # Database documentation
│   │   ├── erd.drawio    # Entity Relationship Diagram
│   │   └── schema.sql    # Database schema
├── static/                # Static files (CSS, JS, Images)
│   ├── css/              # Stylesheets
│   └── images/           # Static images
├── media/                 # User-uploaded files
├── templates/             # HTML templates
├── .env                   # Environment variables (not in git)
├── .env.example          # Example environment configuration
├── .gitignore            # Git ignore rules
├── LICENSE               # Project license
├── README.md             # Project documentation
├── manage.py             # Django management script
└── requirements.txt      # Python dependencies
```

## Development Timeline

### Phase 1 - MVP (Estimated: 4 weeks)

#### Authentication System
- [x] Basic user registration
- [ ] Email verification for new accounts
- [ ] Password reset functionality
- [ ] Login with email verification
- [ ] Session management

#### Customer Management (Basic)
- [ ] Individual customer profiles
- [ ] Business customer profiles
- [ ] Customer recommendation system
- [ ] Basic customer verification

#### Loan Management (Core)
- [ ] Personal loan processing
- [ ] Business loan processing
- [ ] Basic interest calculation
- [ ] Penalty calculation
- [ ] Loan status management
- [ ] Basic repayment processing

#### Account Management
- [ ] Customer loan accounts
- [ ] Basic transaction tracking
- [ ] Simple account statements

### Phase 2 - Enhanced Features (Estimated: 6 weeks)

#### Security Enhancements
- [ ] Two-factor authentication
- [ ] Rate limiting
- [ ] Login attempt tracking
- [ ] Security audit logging
- [ ] Session timeout management

#### Advanced Customer Features
- [ ] Credit scoring system
- [ ] Referral reward system
- [ ] Document management
- [ ] Communication history
- [ ] Customer relationship tracking

#### Advanced Loan Features
- [ ] Loan eligibility criteria
- [ ] Automated payment schedules
- [ ] Payment reminders
- [ ] Loan restructuring
- [ ] Collateral management

#### Financial Management
- [ ] Double-entry bookkeeping
- [ ] GL account management
- [ ] Advanced financial reporting
- [ ] Portfolio analysis

### Phase 3 - Enterprise Features (Estimated: 8 weeks)

#### Audit & Compliance
- [ ] Complete audit trail
- [ ] User action tracking
- [ ] Regulatory reporting
- [ ] Compliance monitoring

#### Advanced Analytics
- [ ] Risk analysis
- [ ] Default prediction
- [ ] Customer behavior analysis
- [ ] Portfolio performance metrics

#### Integration & API
- [ ] REST API development
- [ ] Payment gateway integration
- [ ] SMS notification system
- [ ] External reporting integration

## Technology Stack

- Python 3.12
- Django 5.0
- Supabase PostgreSQL
- Django REST Framework
- Simple JWT Authentication
- MailerSend (Email Service)
- Celery (Task Queue)
- Redis (Message Broker)
- Bootstrap 5 (MVP Frontend)
- React (Phase 2 Frontend)

## Database Schema

### Core Tables
- Users: Authentication and profile details
- Customers: Individual/Business profiles and verification
- Loans: Loan products, applications, and tracking
- Transactions: Payment processing and history
- Accounts: Balance management and statements

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

## Development Guidelines

1. Code Style
   - Follow PEP 8 guidelines
   - Use meaningful variable and function names
   - Add docstrings to all functions and classes
   - Keep functions small and focused

2. Git Workflow
   - Create feature branches from `develop`
   - Use meaningful commit messages
   - Write tests for new features
   - Submit pull requests for review

3. Testing
   - Write unit tests for all new features
   - Maintain minimum 80% code coverage
   - Run tests before committing:
     ```bash
     python manage.py test
     ```

4. Documentation
   - Update README.md for major changes
   - Document all API endpoints
   - Keep ERD and schema docs updated
   - Add inline code comments for complex logic

## Security Considerations

1. Authentication
   - JWT token-based authentication
   - Role-based access control
   - Session management
   - Password policies

2. Data Protection
   - Input validation
   - SQL injection prevention
   - XSS protection
   - CSRF protection

3. API Security
   - Rate limiting
   - Request validation
   - Secure headers
   - CORS configuration

## Support

For support, email [support contact]

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request