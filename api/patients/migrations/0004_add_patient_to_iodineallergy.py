from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0003_patient_is_iodine_contrast_allergic'),
    ]

    operations = [
        migrations.AddField(
            model_name='iodineallergy',
            name='patient',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='iodine_allergy',
                to='patients.patient'
            ),
        ),
    ] 