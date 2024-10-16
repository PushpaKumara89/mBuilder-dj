# Generated by Django 3.2.4 on 2022-04-11 07:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0188_fill_package_handover_documents_project_and_package_activity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='packagehandoverdocument',
            name='package_activity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.packageactivity'),
        ),
        migrations.AlterField(
            model_name='packagehandoverdocument',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.project'),
        ),
    ]
