from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0003_licenseinfo_created_at_licenseinfo_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialization',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='specialization',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ] 