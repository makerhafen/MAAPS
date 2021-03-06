# Generated by Django 3.1.7 on 2021-05-14 01:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('maaps', '0020_auto_20210514_0007'),
    ]

    operations = [
        migrations.AddField(
            model_name='spaceaccesstracking',
            name='spaceRentPayment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='spaceAccessTrackings', to='maaps.spacerentpayment'),
        ),
        migrations.AlterField(
            model_name='machinesession',
            name='tutor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='MachineSessionsTutor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='machinesession',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='MachineSessionsUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='machinesessionpayment',
            name='machinesession',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='machineSessionPayments', to='maaps.machinesession'),
        ),
    ]
