# Generated by Django 3.2.13 on 2022-08-26 01:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0075_alter_proposal_competitive_process'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proposal',
            old_name='competitive_process',
            new_name='generated_competitive_process',
        ),
    ]
