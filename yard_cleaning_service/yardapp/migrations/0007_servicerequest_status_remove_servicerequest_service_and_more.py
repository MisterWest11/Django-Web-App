# Generated by Django 5.1.5 on 2025-01-24 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yardapp', '0006_servicerequest_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicerequest',
            name='status',
            field=models.CharField(default='Pending', max_length=20),
        ),
        migrations.RemoveField(
            model_name='servicerequest',
            name='service',
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='service',
            field=models.ManyToManyField(to='yardapp.service'),
        ),
    ]
