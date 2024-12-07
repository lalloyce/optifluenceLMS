from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0009_fix_missing_fields'),
    ]

    operations = [
        migrations.RunSQL(
            # Drop existing columns if they exist
            """
            ALTER TABLE loans_loanproduct
            DROP COLUMN IF EXISTS term_months,
            DROP COLUMN IF EXISTS grace_period_months,
            DROP COLUMN IF EXISTS insurance_fee,
            DROP COLUMN IF EXISTS penalty_rate,
            DROP COLUMN IF EXISTS required_documents,
            DROP COLUMN IF EXISTS eligibility_criteria;
            """
        ),
        migrations.RunSQL(
            # Add columns with correct definitions
            """
            ALTER TABLE loans_loanproduct
            ADD COLUMN term_months INT NOT NULL DEFAULT 12,
            ADD COLUMN grace_period_months INT NOT NULL DEFAULT 0,
            ADD COLUMN insurance_fee DECIMAL(5,2) NOT NULL DEFAULT 0.00,
            ADD COLUMN penalty_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
            ADD COLUMN required_documents LONGTEXT NULL,
            ADD COLUMN eligibility_criteria LONGTEXT NULL;
            """
        ),
    ]
