# Generated by Django 4.2.17 on 2024-12-07 07:47

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0007_alter_customer_email'),
        ('loans', '0003_loanapplication_loanconfig_repaymentschedule_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoanGuarantor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guarantee_amount', models.DecimalField(decimal_places=2, help_text='Amount guaranteed by this guarantor', max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('guarantee_percentage', models.DecimalField(decimal_places=2, help_text='Percentage of loan amount guaranteed', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('WITHDRAWN', 'Withdrawn')], default='PENDING', max_length=20)),
                ('id_document', models.CharField(blank=True, help_text="Path to guarantor's ID document", max_length=255, null=True)),
                ('income_proof', models.CharField(blank=True, help_text="Path to guarantor's income proof", max_length=255, null=True)),
                ('verified', models.BooleanField(default=False, help_text='Whether the guarantor has been verified')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('guarantor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='guaranteed_loans', to='customers.customer')),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guarantors', to='loans.loan')),
            ],
            options={
                'verbose_name': 'loan guarantor',
                'verbose_name_plural': 'loan guarantors',
                'ordering': ['-created_at'],
                'unique_together': {('loan', 'guarantor')},
            },
        ),
    ]
