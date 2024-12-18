# Generated by Django 4.2.17 on 2024-12-07 17:32

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0011_remove_loanproduct_eligibility_criteria_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanproduct',
            name='eligibility_criteria',
            field=models.JSONField(blank=True, help_text='Eligibility criteria for loan approval', null=True),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='grace_period_months',
            field=models.IntegerField(default=0, help_text='Grace period in months before first payment is due', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='insurance_fee',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Insurance fee as percentage of loan amount', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='penalty_rate',
            field=models.DecimalField(decimal_places=2, default=Decimal('10.00'), help_text='Annual penalty rate for late payments', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='required_documents',
            field=models.JSONField(blank=True, help_text='List of required documents for loan application', null=True),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='term_months',
            field=models.IntegerField(default=1, help_text='Default term length in months', validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
