# Generated by Django 3.2.4 on 2021-11-16 06:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0151_auto_20211112_0712'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetHandoverInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('guid_external_ref', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('warranty', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('manufacture_serial_number', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('model_number', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('asset_handover', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.assethandover')),
            ],
            options={
                'db_table': 'asset_handover_information',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.AddConstraint(
            model_name='assethandoverinformation',
            constraint=models.UniqueConstraint(condition=models.Q(('deleted__isnull', True)), fields=('asset_handover',), name='asset_handover_information_unique'),
        ),
    ]
