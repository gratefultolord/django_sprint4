# Generated by Django 3.2.16 on 2023-09-30 06:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='is_published',
        ),
    ]