# Generated by Django 4.2.17 on 2024-12-07 07:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0003_loanapplication_loanconfig_repaymentschedule_and_more'),
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repaymentschedule',
            name='loan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repayment_schedules', to='loans.loan'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='loan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transaction_records', to='loans.loan'),
        ),
    ]
