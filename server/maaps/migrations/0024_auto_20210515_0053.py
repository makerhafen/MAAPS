# Generated by Django 3.1.7 on 2021-05-15 00:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maaps', '0023_spacerentpayment_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='machinesessionpayment',
            old_name='value',
            new_name='price',
        ),
        migrations.RenameField(
            model_name='materialpayment',
            old_name='value',
            new_name='price',
        ),
        migrations.RenameField(
            model_name='spacerentpayment',
            old_name='value',
            new_name='price',
        ),
    ]
