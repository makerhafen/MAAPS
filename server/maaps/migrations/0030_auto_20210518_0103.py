# Generated by Django 3.1.7 on 2021-05-18 01:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('maaps', '0029_auto_20210518_0018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machinesessionpayment',
            name='machinesession',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='machineSessionPayment', to='maaps.machinesession'),
        ),
    ]
