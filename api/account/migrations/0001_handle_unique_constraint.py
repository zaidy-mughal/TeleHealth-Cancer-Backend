# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # Skip the problematic migration by doing nothing
            "",
            reverse_sql="",
        ),
    ]
