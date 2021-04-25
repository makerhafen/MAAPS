# Generated by Django 3.1.7 on 2021-04-25 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maaps', '0006_auto_20210424_2332'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='show_autologout',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='machinesession',
            name='autologout_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]