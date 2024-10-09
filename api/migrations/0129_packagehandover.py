# Generated by Django 3.2.4 on 2021-08-26 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0128_add_packagehandoverdocumenttype'),
    ]

    operations = [
        migrations.CreateModel(
            name='PackageHandover',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('package_matrix', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.packagematrix')),
            ],
            options={
                'db_table': 'package_handovers',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
