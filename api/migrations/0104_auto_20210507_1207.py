# Generated by Django 3.1.4 on 2021-05-07 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0103_auto_20210505_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtask',
            name='status',
            field=models.CharField(choices=[('closed', 'Closed'), ('in_progress', 'In Progress'), ('removed', 'Removed'), ('contested', 'Contested'), ('under_inspection', 'Under Inspection'), ('inspection_rejected', 'Inspection Rejected'), ('requesting_approval', 'Requesting Approval'), ('requested_approval_rejected', 'Requesting Approval Rejected'), ('declined', 'Declined')], default='in_progress', max_length=255),
        ),
    ]
