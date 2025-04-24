# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # Drop the existing unique index directly
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM pg_indexes
                    WHERE indexname = 'account_emailaddress_user_id_email_987c8728_uniq'
                ) THEN
                    DROP INDEX account_emailaddress_user_id_email_987c8728_uniq;
                END IF;
            END $$;
            """,
            reverse_sql="",
        ),
    ] 