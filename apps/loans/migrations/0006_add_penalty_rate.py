from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0005_alter_loanguarantor_id_document_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanproduct',
            name='penalty_rate',
            field=models.DecimalField(
                decimal_places=2,
                max_digits=5,
                default=0,
                help_text='Annual penalty rate as a percentage',
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100)
                ]
            ),
        ),
    ]
