# Generated by Django 2.2.6 on 2019-10-05 21:44

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('rinja', '0009_auto_20191002_1407'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockposition',
            name='at_date',
        ),
    ]