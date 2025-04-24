# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # First drop the existing unique constraint if it exists
            """
            DO $$
            BEGIN
                -- Drop the unique constraint if it exists
                IF EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conname = 'account_emailaddress_user_id_email_987c8728_uniq'
                ) THEN
                    ALTER TABLE account_emailaddress DROP CONSTRAINT account_emailaddress_user_id_email_987c8728_uniq;
                END IF;

                -- Drop the unique index if it exists
                IF EXISTS (
                    SELECT 1
                    FROM pg_indexes
                    WHERE indexname = 'account_emailaddress_user_id_email_987c8728_uniq'
                ) THEN
                    DROP INDEX account_emailaddress_user_id_email_987c8728_uniq;
                END IF;
            END $$;
            """,
            # No reverse SQL needed
            reverse_sql="",
        ),
    ]
