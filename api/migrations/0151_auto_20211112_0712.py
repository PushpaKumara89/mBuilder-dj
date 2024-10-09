# Generated by Django 3.2.4 on 2021-11-12 07:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0150_auto_20211111_0804'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetHandoverDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('number_required_files', models.IntegerField(default=0)),
                ('asset_handover', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.assethandover')),
                ('document_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.assethandoverdocumenttype')),
            ],
            options={
                'db_table': 'asset_handover_documents',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.AddConstraint(
            model_name='assethandoverdocument',
            constraint=models.UniqueConstraint(condition=models.Q(('deleted__isnull', True)), fields=('asset_handover', 'document_type'), name='asset_handover_document_unique'),
        ),
    ]
