# Generated by Django 3.2.10 on 2021-12-23 07:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0001_initial'),
        ('profile', '__first__'),
        ('core', '0002_auto_20211112_0942'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('discount', models.PositiveIntegerField()),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_event', to='category.category')),
                ('images', models.ManyToManyField(blank=True, related_name='events', to='core.Image')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_event', to='profile.employeeprofile')),
                ('participants', models.ManyToManyField(blank=True, related_name='participated_events', to='profile.UserProfile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
