# Generated by Django 3.1.7 on 2021-05-09 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maaps', '0007_auto_20210425_0132'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='commercial_account',
            field=models.BooleanField(default=False),
        ),
    ]
