# Generated by Django 5.1.7 on 2025-04-15 11:50

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_hospitalbloodrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hospitalbloodrequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('delivered', 'Delivered'), ('failed', 'Failed'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
        migrations.CreateModel(
            name='PasswordReset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reset_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_when', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
