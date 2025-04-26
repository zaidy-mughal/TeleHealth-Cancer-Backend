from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0009_fix_specialization_table'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- No need to modify the id column since it's already UUID
            -- Just ensure the UUID extension is enabled
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            """,
            reverse_sql="""
            -- No reverse operation needed
            """
        ),
    ] 