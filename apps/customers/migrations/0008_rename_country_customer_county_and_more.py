# Generated by Django 4.2.17 on 2024-12-12 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0007_alter_customer_email'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='country',
            new_name='county',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='address',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='postal_code',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='state',
        ),
    ]
