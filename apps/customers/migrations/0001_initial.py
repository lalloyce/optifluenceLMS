# Generated by Django 5.0 on 2024-11-21 12:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')], max_length=10)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('phone_number', models.CharField(max_length=20)),
                ('address', models.TextField()),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=20, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('id_type', models.CharField(max_length=50)),
                ('id_number', models.CharField(max_length=100)),
                ('id_expiry_date', models.DateField(blank=True, null=True)),
                ('employment_status', models.CharField(max_length=50)),
                ('employer_name', models.CharField(blank=True, max_length=255, null=True)),
                ('employer_address', models.TextField(blank=True, null=True)),
                ('employer_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('monthly_income', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('employment_duration', models.IntegerField(blank=True, null=True)),
                ('credit_score', models.IntegerField(blank=True, null=True)),
                ('risk_rating', models.CharField(blank=True, max_length=20, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'customer',
                'verbose_name_plural': 'customers',
                'unique_together': {('id_type', 'id_number')},
            },
        ),
        migrations.CreateModel(
            name='CustomerDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(max_length=50)),
                ('document_path', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='customers.customer')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_customer_documents', to=settings.AUTH_USER_MODEL)),
                ('verified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_customer_documents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'customer document',
                'verbose_name_plural': 'customer documents',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]