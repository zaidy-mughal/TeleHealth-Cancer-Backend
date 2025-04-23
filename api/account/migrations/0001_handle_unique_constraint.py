# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # Drop the existing unique constraint if it exists
            "DROP CONSTRAINT IF EXISTS account_emailaddress_user_id_email_987c8728_uniq;",
            # No reverse SQL needed
            reverse_sql="",
        ),
    ] 