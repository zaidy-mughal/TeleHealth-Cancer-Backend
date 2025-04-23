from django.db import migrations, models
import uuid

def generate_uuid(apps, schema_editor):
    for model_name in [
        'Patient', 'Allergy', 'Medication', 'MedicalHistory',
        'SurgicalHistory', 'CancerType', 'CancerHistory',
        'AddictionHistory', 'PrimaryPhysician', 'Pharmacist'
    ]:
        Model = apps.get_model('patients', model_name)
        for instance in Model.objects.all():
            instance.uuid = uuid.uuid4()
            instance.save()

class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='uuid',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='allergy',
            name='uuid',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='medication',
            name='uuid',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='medicalhistory',
            name='uuid',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='surgicalhistory',
            name='uuid',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='cancertype',
            name='uuid',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='cancerhistory',
            name='uuid',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='addictionhistory',
            name='uuid',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='primaryphysician',
            name='uuid',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='pharmacist',
            name='uuid',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.RunPython(generate_uuid),
        migrations.AlterField(
            model_name='patient',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='allergy',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='medication',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='medicalhistory',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='surgicalhistory',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='cancertype',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='cancerhistory',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='addictionhistory',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='primaryphysician',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='pharmacist',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
    ] 