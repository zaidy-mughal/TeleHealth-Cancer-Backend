from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0003_add_uuid_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patient',
            name='id',
        ),
        migrations.RemoveField(
            model_name='allergy',
            name='id',
        ),
        migrations.RemoveField(
            model_name='medication',
            name='id',
        ),
        migrations.RemoveField(
            model_name='medicalhistory',
            name='id',
        ),
        migrations.RemoveField(
            model_name='surgicalhistory',
            name='id',
        ),
        migrations.RemoveField(
            model_name='cancertype',
            name='id',
        ),
        migrations.RemoveField(
            model_name='cancerhistory',
            name='id',
        ),
        migrations.RemoveField(
            model_name='addictionhistory',
            name='id',
        ),
        migrations.RemoveField(
            model_name='primaryphysician',
            name='id',
        ),
        migrations.RemoveField(
            model_name='pharmacist',
            name='id',
        ),
        migrations.AlterField(
            model_name='patient',
            name='uuid',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='allergy',
            name='uuid',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='medication',
            name='uuid',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='medicalhistory',
            name='uuid',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='surgicalhistory',
            name='uuid',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='cancertype',
            name='uuid',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='cancerhistory',
            name='uuid',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='addictionhistory',
            name='uuid',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='primaryphysician',
            name='uuid',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='pharmacist',
            name='uuid',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False),
        ),
    ] 