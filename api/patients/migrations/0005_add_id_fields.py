from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0004_make_uuid_primary_key'),
    ]

    operations = [
        # First add id fields as non-primary keys
        migrations.AddField(
            model_name='patient',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='iodineallergy',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='allergy',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='medication',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='medicalhistory',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='surgicalhistory',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='cancertype',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='cancerhistory',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='addictionhistory',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='primaryphysician',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='pharmacist',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        # Then make id fields primary keys
        migrations.AlterField(
            model_name='patient',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='iodineallergy',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='allergy',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='medication',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='medicalhistory',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='surgicalhistory',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='cancertype',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='cancerhistory',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='addictionhistory',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='primaryphysician',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='pharmacist',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
    ] 