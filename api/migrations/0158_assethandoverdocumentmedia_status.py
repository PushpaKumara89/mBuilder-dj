# Generated by Django 3.2.4 on 2021-11-29 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0157_add_multiplex_documents_types_20211129_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='assethandoverdocumentmedia',
            name='status',
            field=models.CharField(choices=[('in_progress', 'In Progress'), ('contested', 'Contested'), ('requesting_approval', 'Requesting Approval'), ('requested_approval_rejected', 'Requested Approval Rejected'), ('accepted', 'Accepted')], default='in_progress', max_length=255),
            preserve_default=False,
        ),
    ]
