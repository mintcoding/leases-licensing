# Generated by Django 3.2.13 on 2022-09-29 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0101_rename_financialyear_consumerpriceindex'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumerpriceindex',
            name='cpi_value_q2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='consumerpriceindex',
            name='cpi_value_q3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='consumerpriceindex',
            name='cpi_value_q4',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
