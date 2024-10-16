# Generated by Django 3.2.4 on 2021-08-25 11:46

from django.db import migrations, models
import django.db.models.deletion

from api.models import PackageHandoverDocumentType


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0126_add_packagehandoverdocumentgroups'),
    ]

    operations = [
        migrations.CreateModel(
            name='PackageHandoverDocumentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.packagehandoverdocumentgroup')),
            ],
            options={
                'db_table': 'package_handover_document_types',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
