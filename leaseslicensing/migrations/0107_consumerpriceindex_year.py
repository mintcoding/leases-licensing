# Generated by Django 3.2.13 on 2022-09-30 01:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0106_auto_20220929_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumerpriceindex',
            name='year',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
