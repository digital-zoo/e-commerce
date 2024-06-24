from django.db import models
from customer.models import MyUser
from django.utils import timezone
# from django.contrib.auth.models import BaseUserManager
from customer.models import MyUser
from django.contrib.auth.models import Group, Permission

# Myuser 상속받아서 seller 테이블 생성    
class Seller(MyUser):    
    company_name = models.CharField(max_length=50)    
    business_contact = models.CharField(max_length=50,unique=True,null=True)
    registration_number = models.CharField(max_length=50,unique=True)

    groups = models.ManyToManyField(Group, related_name='seller_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='seller_permissions_set', blank=True)

    class Meta:
        verbose_name = 'Seller'
        verbose_name_plural = 'Sellers'

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories') # 상위 카테고리 삭제 시 null로 설정

    def __str__(self):
        return self.category_name

from django.utils import timezone

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True) # 셀러 삭제 시 null로 설정
    seller_id_copy = models.IntegerField()  # 셀러 ID를 직접 저장
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    product_name = models.CharField(max_length=255)
    price = models.IntegerField(default=0)
    description = models.TextField()
    is_visible = models.BooleanField(default=True)
    stock = models.IntegerField()
    discount_rate = models.DecimalField(max_digits=3, decimal_places=2)
    is_option = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def category_name(self):
        return self.category.category_name

    def save(self, *args, **kwargs):
        if self.seller:
            self.seller_id_copy = self.seller.id  # 판매자 ID 저장
        super(Product, self).save(*args, **kwargs)

class ProductImage(models.Model):
    productimage_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url=models.URLField()
 
    def __str__(self):
        return f"Image for {self.product.product_name} at {self.image_url}"
