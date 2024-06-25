# Generated by Django 5.0.4 on 2024-06-24 18:49

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('like_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('membership_id', models.IntegerField(primary_key=True, serialize=False)),
                ('grade', models.CharField(max_length=50, unique=True)),
                ('member_discount_rate', models.DecimalField(decimal_places=2, max_digits=3)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('customer_id_copy', models.IntegerField()),
                ('order_date', models.DateField()),
                ('order_status', models.CharField(max_length=50)),
                ('shipping_address', models.CharField(max_length=300)),
                ('postal_code', models.CharField(max_length=5)),
                ('recipient', models.CharField(max_length=100)),
                ('recipient_phone_number', models.CharField(max_length=20)),
                ('payment_method', models.CharField(max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('orderitem_id', models.AutoField(primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=100)),
                ('product_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
                ('is_refunded', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_id', models.AutoField(primary_key=True, serialize=False)),
                ('paid_amount', models.IntegerField(default=0)),
                ('imp_uid', models.CharField(max_length=100)),
                ('merchant_uid', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('review_id', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('rating', models.IntegerField(default=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('shippingaddress_id', models.AutoField(primary_key=True, serialize=False)),
                ('shipping_address_name', models.CharField(max_length=20)),
                ('shipping_address', models.CharField(max_length=300)),
                ('shipping_address_detail', models.CharField(max_length=300)),
                ('postal_code', models.CharField(max_length=5)),
                ('recipient', models.CharField(max_length=100)),
                ('recipient_phone_number', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=50, unique=True)),
                ('email', models.EmailField(max_length=50, unique=True, validators=[django.core.validators.EmailValidator(message='이미 등록된 이메일 주소입니다.')])),
                ('phone_number', models.CharField(max_length=11, unique=True, validators=[django.core.validators.RegexValidator(message='휴대폰 번호 형식이 올바르지 않습니다.', regex='^(01[016789]\\d{7,8})$')])),
                ('is_staff', models.BooleanField(default=False)),
                ('customer_name', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=50, null=True)),
                ('postal_code', models.CharField(max_length=50, null=True)),
                ('is_snsid', models.BooleanField(default=False)),
                ('is_advertise', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, related_name='customer_set', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='customer_permissions_set', to='auth.permission')),
            ],
            options={
                'verbose_name': 'Customer',
                'verbose_name_plural': 'Customers',
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('cart_id', models.AutoField(primary_key=True, serialize=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('cartitem_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.cart')),
            ],
        ),
    ]
