# Generated by Django 5.1.7 on 2025-03-10 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_alter_customuser_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('1', 'HOD'), ('2', 'Staff'), ('3', 'Student')], default=1, max_length=1),
        ),
    ]
