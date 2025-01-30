# Generated by Django 5.1.5 on 2025-01-30 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yardapp', '0009_rename_service_servicerequest_services'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='profile_pic',
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], default='Pending', max_length=20),
        ),
    ]
