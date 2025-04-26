from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0009_fix_specialization_table'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE doctors_doctor 
            DROP CONSTRAINT doctors_doctor_pkey CASCADE;
            ALTER TABLE doctors_doctor 
            DROP COLUMN id,
            ADD COLUMN id UUID PRIMARY KEY DEFAULT gen_random_uuid();
            """,
            reverse_sql="""
            ALTER TABLE doctors_doctor 
            DROP CONSTRAINT doctors_doctor_pkey CASCADE;
            ALTER TABLE doctors_doctor 
            DROP COLUMN id,
            ADD COLUMN id SERIAL PRIMARY KEY;
            """
        ),
    ] 