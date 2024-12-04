# Generated by Django 5.1.3 on 2024-11-21 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_businessprofile_customer_customer_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessprofile',
            name='incorporation_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='businessprofile',
            name='industry',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='businessprofile',
            name='primary_contact_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='businessprofile',
            name='registration_number',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='businessprofile',
            name='tax_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='businessprofile',
            name='years_in_business',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='businessprofile',
            index=models.Index(fields=['business_name', 'business_type'], name='customers_b_busines_5b9861_idx'),
        ),
        migrations.AddIndex(
            model_name='businessprofile',
            index=models.Index(fields=['primary_contact_name', 'primary_contact_phone'], name='customers_b_primary_74fdef_idx'),
        ),
    ]
