# Generated by Django 5.0.3 on 2024-04-29 13:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0003_shippingaddress_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='myuser_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='customer.myuser'),
        ),
    ]
