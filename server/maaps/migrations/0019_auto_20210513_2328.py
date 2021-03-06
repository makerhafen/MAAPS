# Generated by Django 3.1.7 on 2021-05-13 23:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('maaps', '0018_auto_20210511_2325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spacerentpayment',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='spaceRentPayments', to='maaps.invoice'),
        ),
        migrations.AlterField(
            model_name='spacerentpayment',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='spaceRentPayments', to='maaps.transaction'),
        ),
        migrations.AlterField(
            model_name='spacerentpayment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spaceRentPayments', to=settings.AUTH_USER_MODEL, verbose_name='Benutzer'),
        ),
        migrations.CreateModel(
            name='SpaceAccessTracking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='spaceAccessTrackings', to='maaps.invoice')),
                ('transaction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='spaceAccessTrackings', to='maaps.transaction')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spaceAccessTrackings', to=settings.AUTH_USER_MODEL, verbose_name='Benutzer')),
            ],
        ),
    ]
