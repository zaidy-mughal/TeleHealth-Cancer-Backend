from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0007_add_timestamp_to_specialization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialization',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True),
        ),
    ] 