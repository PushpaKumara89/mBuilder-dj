# Generated by Django 3.2.4 on 2021-12-01 06:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0160_alter_assethandoverdocumentmedia_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='assethandoverdocumentmedia',
            name='last_confirmed_update',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.assethandoverdocumentmediaupdate'),
        ),
        migrations.AlterField(
            model_name='packagehandoverdocumentmedia',
            name='last_confirmed_update',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.packagehandoverdocumentmediaupdate'),
        ),
        migrations.AlterField(
            model_name='qualityissue',
            name='last_confirmed_update',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.qualityissueupdate'),
        ),
        migrations.AlterField(
            model_name='subtask',
            name='last_confirmed_update',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_subtask', to='api.subtaskupdate'),
        ),
    ]
