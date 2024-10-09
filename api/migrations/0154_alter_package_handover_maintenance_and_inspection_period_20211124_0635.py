# Generated by Django 3.2.4 on 2021-11-24 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0153_merge_0152_auto_20211115_0625_0152_auto_20211116_0647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='packagehandover',
            name='inspection_period',
            field=models.IntegerField(choices=[(None, 'Undefined'), (0, 'Not Required'), (1, 'One'), (3, 'Three'), (6, 'Six'), (12, 'Twelve'), (18, 'Eighteen')], default=None, null=True),
        ),
        migrations.AlterField(
            model_name='packagehandover',
            name='maintenance_period',
            field=models.IntegerField(choices=[(None, 'Undefined'), (0, 'Not Required'), (1, 'One'), (3, 'Three'), (6, 'Six'), (12, 'Twelve'), (18, 'Eighteen')], default=None, null=True),
        ),
    ]
