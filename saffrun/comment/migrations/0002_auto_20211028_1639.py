# Generated by Django 3.2.8 on 2021-10-28 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comment", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="comment",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
