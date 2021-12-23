# Generated by Django 3.2.10 on 2021-12-23 08:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20211112_0942'),
        ('profile', '0002_auto_20211223_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeprofile',
            name='avatar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.image'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.image'),
        ),
    ]
