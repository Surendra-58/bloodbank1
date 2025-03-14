# Generated by Django 5.1.6 on 2025-03-13 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_alter_customuser_first_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='blood_group',
            field=models.CharField(blank=True, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], default='A+', max_length=4, null=True),
        ),
    ]
