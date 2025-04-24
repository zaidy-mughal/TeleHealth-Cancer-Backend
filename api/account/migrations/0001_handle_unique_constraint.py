# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # Drop all possible constraints and indexes
            """
            DO $$
            BEGIN
                -- Drop all possible constraints
                FOR r IN (
                    SELECT conname
                    FROM pg_constraint
                    WHERE conrelid = 'account_emailaddress'::regclass
                ) LOOP
                    EXECUTE format('ALTER TABLE account_emailaddress DROP CONSTRAINT IF EXISTS %I', r.conname);
                END LOOP;

                -- Drop all possible indexes
                FOR r IN (
                    SELECT indexname
                    FROM pg_indexes
                    WHERE tablename = 'account_emailaddress'
                ) LOOP
                    EXECUTE format('DROP INDEX IF EXISTS %I', r.indexname);
                END LOOP;
            END $$;
            """,
            # No reverse SQL needed
            reverse_sql="",
        ),
    ]
