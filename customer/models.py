from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model
from myuser.models import MyUser
from django.contrib.auth.models import Group, Permission

# 멤버쉽 테이블\\
class Membership(models.Model):
    membership_id = models.IntegerField(primary_key=True)
    grade = models.CharField(max_length=50,unique=True)
    member_discount_rate = models.DecimalField(max_digits=3, decimal_places=2)      

# 3단계, 상위 유저 클래스를 상속받는 customer 클래스 생성    
class Customer(MyUser):    
    membership = models.ForeignKey(Membership, on_delete=models.DO_NOTHING,default=1)    
    customer_name = models.CharField(max_length=50)    
    address = models.CharField(max_length=50, null=True)
    postal_code = models.CharField(max_length=50, null=True)
    is_snsid = models.BooleanField(default=False)
    is_advertise = models.BooleanField(default=False) # 광고 동의 여부

    groups = models.ManyToManyField(Group, related_name='customer_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customer_permissions_set', blank=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

# 카트 테이블
class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)  # 카트ID는 자동으로 생성되는 순차적인 정수
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Customer 테이블과 외래키 관계, 

# 카트 아이템 테이블
class CartItem(models.Model):
    cartitem_id = models.AutoField(primary_key=True)  # 카트아이템ID는 자동으로 생성되는 순차적인 정수
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)  # 카트와의 외래키 관계, 카트가 삭제되면 관련된 카트아이템도 삭제
    product = models.ForeignKey('seller.Product', on_delete=models.CASCADE)  # product와 외래키 관계, 
    quantity = models.IntegerField()  # 수량은 정수형

    def get_total_price(self): # 한 유저의 카트에 담긴 총 금액을 출력하기 위한 메서드
        return int(self.quantity * self.product.price * (1 - (self.product.discount_rate)))
    
class Order(models.Model):
    order_id = models.AutoField(primary_key=True) 
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)  # 고객 삭제 시 null로 설정
    customer_id_copy = models.IntegerField()  # 고객 ID를 직접 저장
    order_date = models.DateField()
    order_status = models.CharField(max_length=50)
    shipping_address = models.CharField(max_length=300)
    postal_code = models.CharField(max_length=5)
    recipient = models.CharField(max_length=100)
    recipient_phone_number = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order_id)

    def save(self, *args, **kwargs):
        if self.customer:
            self.customer_id_copy = self.customer.id  # 고객 ID 저장
        super(Order, self).save(*args, **kwargs)

class OrderItem(models.Model):
    orderitem_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('seller.Product', on_delete=models.SET_NULL, null=True)  # 상품 삭제 시 null로 설정
    product_name = models.CharField(max_length=100)  # 주문 당시의 상품 이름을 저장
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # 주문 당시의 상품 가격을 저장
    quantity = models.IntegerField() 

    def __str__(self):
        return str(self.orderitem_id)

    def save(self, *args, **kwargs):
        if self.product:
            self.product_name = self.product.product_name
            self.product_price = self.product.price
        super(OrderItem, self).save(*args, **kwargs)
    
class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    paid_amount = models.IntegerField(default=0)
    imp_uid = models.CharField(max_length=100)
    merchant_uid = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    like_id = models.AutoField(primary_key=True)
    product = models.ForeignKey('seller.Product', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)    
    
    class Meta:
        ordering = ['-created_at']

class ShippingAddress(models.Model):
    shippingaddress_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shipping_address_name = models.CharField(max_length=20)
    shipping_address = models.CharField(max_length=300)
    postal_code = models.CharField(max_length=5)
    recipient = models.CharField(max_length=100)
    recipient_phone_number = models.CharField(max_length=20)

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)  # 고객 삭제 시 null로 설정
    customer_id_copy = models.IntegerField()  # 고객 ID를 직접 저장
    product = models.ForeignKey('seller.Product', on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.customer:
            self.customer_id_copy = self.customer.id  # 고객 ID 저장
        super(Review, self).save(*args, **kwargs)
