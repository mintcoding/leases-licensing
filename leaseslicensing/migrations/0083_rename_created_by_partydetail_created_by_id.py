# Generated by Django 3.2.13 on 2022-09-02 06:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leaseslicensing', '0082_temporarydocument_temporarydocumentcollection'),
    ]

    operations = [
        migrations.RenameField(
            model_name='partydetail',
            old_name='created_by',
            new_name='created_by_id',
        ),
    ]
