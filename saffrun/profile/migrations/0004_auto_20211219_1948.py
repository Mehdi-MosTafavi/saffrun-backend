# Generated by Django 3.2.8 on 2021-12-19 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0003_auto_20211112_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeprofile',
            name='city',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='city',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]