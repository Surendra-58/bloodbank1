# Generated by Django 5.1.7 on 2025-03-12 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_customuser_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='blood_group',
            field=models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], default='A+', max_length=3),
        ),
        migrations.AddField(
            model_name='customuser',
            name='contact_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='dob',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='identity',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_organization',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='organization_name',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('1', 'Admin'), ('2', 'Hospital'), ('3', 'User')], default=1, max_length=1),
        ),
    ]
