# Generated by Django 5.1.5 on 2025-01-23 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yardapp', '0005_rename_preferred_date_servicerequest_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicerequest',
            name='address',
            field=models.CharField(default='Address not provided', max_length=100),
            preserve_default=False,
        ),
    ]
