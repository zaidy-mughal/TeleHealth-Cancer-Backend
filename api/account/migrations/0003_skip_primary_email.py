# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_skip_email_index'),
    ]

    operations = [
        migrations.RunSQL(
            # Skip the problematic migration by doing nothing
            "",
            reverse_sql="",
        ),
    ] 