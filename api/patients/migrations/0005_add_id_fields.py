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
        migrations.AddField(
            model_name='patient',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AddField(
            model_name='iodineallergy',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AddField(
            model_name='allergy',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AddField(
            model_name='medication',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AddField(
            model_name='medicalhistory',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AddField(
            model_name='surgicalhistory',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AddField(
            model_name='cancertype',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AddField(
            model_name='cancerhistory',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AddField(
            model_name='addictionhistory',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AddField(
            model_name='primaryphysician',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AddField(
            model_name='pharmacist',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.RunPython(gen_uuid),
    ] 