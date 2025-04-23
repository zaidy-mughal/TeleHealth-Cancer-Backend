from django.db import migrations, models
import uuid

def gen_uuid(apps, schema_editor):
    for model_name in [
        'Patient', 'IodineAllergy', 'Allergy', 'Medication', 'MedicalHistory',
        'SurgicalHistory', 'CancerType', 'CancerHistory', 'AddictionHistory',
        'PrimaryPhysician', 'Pharmacist'
    ]:
        Model = apps.get_model('patients', model_name)
        for row in Model.objects.all():
            row.id = uuid.uuid4()
            row.save(update_fields=['id'])

class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0004_make_uuid_primary_key'),
    ]

    operations = [
        migrations.RunPython(gen_uuid),
    ] 