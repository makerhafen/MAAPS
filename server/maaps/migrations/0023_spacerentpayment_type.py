# Generated by Django 3.1.7 on 2021-05-14 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maaps', '0022_auto_20210514_0237'),
    ]

    operations = [
        migrations.AddField(
            model_name='spacerentpayment',
            name='type',
            field=models.CharField(default='monthly', max_length=10000),
        ),
    ]
