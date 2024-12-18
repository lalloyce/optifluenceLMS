# Generated by Django 5.0 on 2024-11-22 09:37

from django.db import migrations, models

def set_default_email(apps, schema_editor):
    Customer = apps.get_model('customers', 'Customer')
    for customer in Customer.objects.filter(email__isnull=True):
        customer.email = f'customer_{customer.id}@example.com'
        customer.save()

class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0005_remove_customer_customers_c_full_na_5acde0_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(set_default_email),
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
