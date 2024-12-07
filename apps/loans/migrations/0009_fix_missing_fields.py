from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0008_remove_loanproduct_eligibility_criteria_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanproduct',
            name='term_months',
            field=models.IntegerField(default=12, help_text='Loan term in months'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='grace_period_months',
            field=models.IntegerField(default=0, help_text='Grace period in months before first payment is due'),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='insurance_fee',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Insurance fee as a percentage of loan amount', max_digits=5),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='penalty_rate',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Annual penalty rate as a percentage', max_digits=5),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='required_documents',
            field=models.TextField(blank=True, default='', help_text='List of required documents (one per line)'),
        ),
        migrations.AddField(
            model_name='loanproduct',
            name='eligibility_criteria',
            field=models.TextField(blank=True, default='', help_text='Eligibility requirements (one per line)'),
        ),
    ]
