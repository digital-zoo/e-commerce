# Generated by Django 5.0.3 on 2024-04-24 04:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('myuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('company_name', models.CharField(max_length=255)),
                ('business_contact', models.CharField(max_length=255, null=True, unique=True)),
                ('registration_number', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('customer.myuser',),
        ),
    ]
