# Generated by Django 5.1.3 on 2024-11-21 23:44

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_customer_is_active'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_name', models.CharField(max_length=255)),
                ('business_type', models.CharField(choices=[('SOLE_PROPRIETORSHIP', 'Sole Proprietorship'), ('PARTNERSHIP', 'Partnership'), ('CORPORATION', 'Corporation'), ('LLC', 'Limited Liability Company'), ('OTHER', 'Other')], max_length=50)),
                ('registration_number', models.CharField(max_length=100, unique=True)),
                ('tax_id', models.CharField(max_length=100, unique=True)),
                ('incorporation_date', models.DateField()),
                ('industry', models.CharField(max_length=100)),
                ('website', models.URLField(blank=True, null=True)),
                ('annual_revenue', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('number_of_employees', models.IntegerField(blank=True, null=True)),
                ('years_in_business', models.IntegerField()),
                ('primary_contact_name', models.CharField(max_length=255)),
                ('primary_contact_position', models.CharField(max_length=100)),
                ('primary_contact_phone', models.CharField(max_length=20)),
                ('primary_contact_email', models.EmailField(max_length=254)),
                ('business_description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'business profile',
                'verbose_name_plural': 'business profiles',
            },
        ),
        migrations.AddField(
            model_name='customer',
            name='customer_type',
            field=models.CharField(choices=[('INDIVIDUAL', 'Individual'), ('BUSINESS', 'Business')], default='INDIVIDUAL', max_length=20),
        ),
        migrations.AddField(
            model_name='customer',
            name='last_recommendation_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='recommendation_score',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='customer',
            name='recommended_products',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='verification_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='verification_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('VERIFIED', 'Verified'), ('REJECTED', 'Rejected')], default='PENDING', max_length=20),
        ),
        migrations.AddField(
            model_name='customer',
            name='verified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='verified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_customers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='customerdocument',
            name='verification_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_customers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='customer',
            name='credit_score',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(300), django.core.validators.MaxValueValidator(850)]),
        ),
        migrations.AlterField(
            model_name='customer',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='employment_status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='id_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='id_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='customerdocument',
            name='document_type',
            field=models.CharField(choices=[('ID_PROOF', 'ID Proof'), ('ADDRESS_PROOF', 'Address Proof'), ('INCOME_PROOF', 'Income Proof'), ('BUSINESS_REGISTRATION', 'Business Registration'), ('TAX_DOCUMENT', 'Tax Document'), ('OTHER', 'Other')], max_length=50),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['full_name', 'phone_number'], name='customers_c_full_na_5acde0_idx'),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['customer_type', 'is_active'], name='customers_c_custome_5cafca_idx'),
        ),
        migrations.AddField(
            model_name='businessprofile',
            name='customer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='business_profile', to='customers.customer'),
        ),
    ]