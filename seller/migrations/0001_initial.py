# Generated by Django 5.0.4 on 2024-04-26 18:02

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
        migrations.CreateModel(
            name='Category',
            fields=[
                ('category_id', models.AutoField(primary_key=True, serialize=False)),
                ('category_name', models.CharField(max_length=100)),
                ('parent_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='seller.category')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.AutoField(primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=255)),
                ('price', models.IntegerField(default=0)),
                ('description', models.TextField()),
                ('is_visible', models.BooleanField(default=True)),
                ('stock', models.IntegerField()),
                ('discount_rate', models.DecimalField(decimal_places=2, max_digits=3)),
                ('is_option', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='seller.category')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seller.seller')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('productimage_id', models.AutoField(primary_key=True, serialize=False)),
                ('image_url', models.URLField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='seller.product')),
            ],
        ),
    ]
