# Generated by Django 5.1.5 on 2025-01-27 09:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yardapp', '0008_remove_servicerequest_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='servicerequest',
            old_name='service',
            new_name='services',
        ),
    ]
