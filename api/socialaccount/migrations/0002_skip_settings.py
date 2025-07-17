# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialaccount', '0001_skip_provider_id'),
    ]

    operations = [
        migrations.RunSQL(
            # Skip the problematic migration by doing nothing
            "",
            reverse_sql="",
        ),
    ] 