# Generated by Django 5.1.7 on 2025-03-12 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_customuser_blood_group_customuser_contact_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_organization',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('1', 'Admin'), ('2', 'Hospital'), ('3', 'User')], default=3, max_length=1),
        ),
    ]
