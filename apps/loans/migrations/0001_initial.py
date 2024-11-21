# Generated by Django 5.0 on 2024-11-21 12:10

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LoanProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('interest_rate', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('minimum_amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('maximum_amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('minimum_term', models.IntegerField()),
                ('maximum_term', models.IntegerField()),
                ('processing_fee', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'loan product',
                'verbose_name_plural': 'loan products',
            },
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_number', models.CharField(max_length=50, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('term_months', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('interest_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('processing_fee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('application_date', models.DateTimeField(auto_now_add=True)),
                ('approval_date', models.DateTimeField(blank=True, null=True)),
                ('disbursement_date', models.DateTimeField(blank=True, null=True)),
                ('maturity_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('PENDING', 'Pending Approval'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('DISBURSED', 'Disbursed'), ('CLOSED', 'Closed'), ('DEFAULTED', 'Defaulted')], default='DRAFT', max_length=20)),
                ('purpose', models.TextField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='loans', to='customers.customer')),
                ('loan_officer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='handled_loans', to=settings.AUTH_USER_MODEL)),
                ('loan_product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='loans', to='loans.loanproduct')),
            ],
            options={
                'verbose_name': 'loan',
                'verbose_name_plural': 'loans',
                'ordering': ['-application_date'],
            },
        ),
        migrations.CreateModel(
            name='LoanDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(choices=[('APPLICATION', 'Loan Application'), ('AGREEMENT', 'Loan Agreement'), ('COLLATERAL', 'Collateral Document'), ('OTHER', 'Other')], max_length=20)),
                ('document_path', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=200)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='loans.loan')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='uploaded_loan_documents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'loan document',
                'verbose_name_plural': 'loan documents',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]