from django.db import migrations, models
from django.core.validators import MinValueValidator
from decimal import Decimal

def populate_risk_amounts(apps, schema_editor):
    LoanProduct = apps.get_model('loans', 'LoanProduct')
    for loan_product in LoanProduct.objects.all():
        # Set risk-based amounts as a percentage of maximum_amount
        loan_product.high_risk_max_amount = loan_product.maximum_amount * Decimal('0.3')  # 30% of max
        loan_product.medium_risk_max_amount = loan_product.maximum_amount * Decimal('0.6')  # 60% of max
        loan_product.moderate_risk_max_amount = loan_product.maximum_amount * Decimal('0.8')  # 80% of max
        loan_product.save()

def reverse_populate(apps, schema_editor):
    LoanProduct = apps.get_model('loans', 'LoanProduct')
    LoanProduct.objects.all().update(
        high_risk_max_amount=Decimal('0'),
        medium_risk_max_amount=Decimal('0'),
        moderate_risk_max_amount=Decimal('0')
    )

class Migration(migrations.Migration):
    dependencies = [
        ('loans', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanproduct',
            name='high_risk_max_amount',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                default=0,
                validators=[MinValueValidator(0)],
                help_text='Maximum amount for high-risk loans (score < 40)'
            ),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='medium_risk_max_amount',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                default=0,
                validators=[MinValueValidator(0)],
                help_text='Maximum amount for medium-risk loans (score 40-59)'
            ),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='moderate_risk_max_amount',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                default=0,
                validators=[MinValueValidator(0)],
                help_text='Maximum amount for moderate-risk loans (score 60-79)'
            ),
        ),
        migrations.RunPython(populate_risk_amounts, reverse_populate),
    ]
