# Generated by Django 3.2.4 on 2022-07-05 12:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0210_auto_20220630_0508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assethandoverstatistics',
            name='asset_handover_document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.assethandoverdocument'),
        ),
        migrations.AlterField(
            model_name='packagehandoverstatistics',
            name='package_handover_document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.packagehandoverdocument'),
        ),
    ]
