# Generated by Django 4.2.17 on 2024-12-07 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_add_audit_log_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email_verification_token',
            field=models.CharField(blank=True, help_text='Token for email verification', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email_verification_token_created',
            field=models.DateTimeField(blank=True, help_text='When the email verification token was created', null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_email_verified',
            field=models.BooleanField(default=False, help_text='Designates whether this user has verified their email address.', verbose_name='email verified'),
        ),
    ]
