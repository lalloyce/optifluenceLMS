# Generated by Django 4.2.17 on 2024-12-07 19:56

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0015_alter_repaymentschedule_loan'),
        ('customers', '0007_alter_customer_email'),
        ('transactions', '0002_alter_repaymentschedule_loan_alter_transaction_loan'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='description',
        ),
        migrations.AddField(
            model_name='transaction',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='customers.customer'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='loan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='loans.loan'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='reference_number',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('MOBILE_MONEY', 'Mobile Money'), ('BANK_TRANSFER', 'Bank Transfer'), ('CASH', 'Cash'), ('CHECK', 'Check'), ('OTHER', 'Other'), ('DISBURSEMENT', 'Loan Disbursement'), ('REPAYMENT', 'Loan Repayment'), ('PENALTY', 'Late Payment Penalty'), ('FEE', 'Processing Fee')], max_length=20),
        ),
    ]
