from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0008_fix_specialization_id'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE doctors_doctor DROP CONSTRAINT doctors_doctor_specialization_id_0a597af3_fk_doctors_s;
            ALTER TABLE doctors_doctor ADD COLUMN specialization_id_new uuid;
            UPDATE doctors_doctor SET specialization_id_new = gen_random_uuid();
            ALTER TABLE doctors_doctor DROP COLUMN specialization_id;
            ALTER TABLE doctors_doctor RENAME COLUMN specialization_id_new TO specialization_id;
            ALTER TABLE doctors_specialization 
            DROP COLUMN id,
            ADD COLUMN id UUID PRIMARY KEY DEFAULT gen_random_uuid();
            ALTER TABLE doctors_doctor ADD CONSTRAINT doctors_doctor_specialization_id_fk 
            FOREIGN KEY (specialization_id) REFERENCES doctors_specialization(id);
            """,
            reverse_sql="""
            ALTER TABLE doctors_doctor DROP CONSTRAINT doctors_doctor_specialization_id_fk;
            ALTER TABLE doctors_doctor ADD COLUMN specialization_id_new bigint;
            UPDATE doctors_doctor SET specialization_id_new = 1;
            ALTER TABLE doctors_doctor DROP COLUMN specialization_id;
            ALTER TABLE doctors_doctor RENAME COLUMN specialization_id_new TO specialization_id;
            ALTER TABLE doctors_specialization 
            DROP COLUMN id,
            ADD COLUMN id SERIAL PRIMARY KEY;
            ALTER TABLE doctors_doctor ADD CONSTRAINT doctors_doctor_specialization_id_0a597af3_fk_doctors_s 
            FOREIGN KEY (specialization_id) REFERENCES doctors_specialization(id);
            """
        ),
    ] 