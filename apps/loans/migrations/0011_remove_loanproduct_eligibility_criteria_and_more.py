# Generated by Django 4.2.17 on 2024-12-07 17:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0010_reset_loanproduct_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loanproduct',
            name='eligibility_criteria',
        ),
        migrations.RemoveField(
            model_name='loanproduct',
            name='grace_period_months',
        ),
        migrations.RemoveField(
            model_name='loanproduct',
            name='insurance_fee',
        ),
        migrations.RemoveField(
            model_name='loanproduct',
            name='penalty_rate',
        ),
        migrations.RemoveField(
            model_name='loanproduct',
            name='required_documents',
        ),
        migrations.RemoveField(
            model_name='loanproduct',
            name='term_months',
        ),
    ]