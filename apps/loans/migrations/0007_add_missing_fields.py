from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0006_add_penalty_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanproduct',
            name='term_months',
            field=models.PositiveIntegerField(
                default=12,
                help_text='Loan term in months'
            ),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='grace_period_months',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Grace period in months before first payment is due'
            ),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='insurance_fee',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=5,
                default=0,
                help_text='Insurance fee as a percentage of loan amount'
            ),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='required_documents',
            field=models.TextField(
                blank=True,
                help_text='List of required documents (one per line)'
            ),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='eligibility_criteria',
            field=models.TextField(
                blank=True,
                help_text='Eligibility requirements (one per line)'
            ),
        ),
    ]
