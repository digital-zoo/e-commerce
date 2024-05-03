# Generated by Django 5.0.3 on 2024-04-29 13:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_alter_customer_myuser_ptr'),
        ('seller', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seller',
            name='myuser_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='customer.myuser'),
        ),
    ]