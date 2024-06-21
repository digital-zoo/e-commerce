from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model

# 멤버쉽 테이블\\
class Membership(models.Model):
    membership_id = models.IntegerField(primary_key=True)
    grade = models.CharField(max_length=255,unique=True)
    member_discount_rate = models.DecimalField(max_digits=3, decimal_places=2)    

###############
# 유저 테이블 커스터 마이징을 위한 3단계
# 1단계, user manager 정의
class MyUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        """
        일반 사용자 생성
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        """
        슈퍼유저 생성
        """
        user = self.create_user(
            username,
            email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True        
        user.save(using=self._db)
        return user
    
# 2단계, 상위 유저 생성   
class MyUser(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=255, unique=True)
    is_staff = models.BooleanField(default=False)  # 관리자 사이트 접근 권한

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email'] #superusercreate할 때 email,phone_number 필요

    objects = MyUserManager()


    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # 슈퍼유저에게는 모든 권한을 부여
        return self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # 슈퍼유저 또는 모든 앱에 대해 True를 반환
        return self.is_superuser

    def __str__(self):
        return self.username
    

# 3단계, 상위 유저 클래스를 상속받는 customer 클래스 생성    
class Customer(MyUser):    
    membership = models.ForeignKey(Membership, on_delete=models.DO_NOTHING)    
    customer_name = models.CharField(max_length=255)    
    address = models.CharField(max_length=255, null=True)
    postal_code = models.CharField(max_length=255, null=True)
    is_snsid = models.BooleanField(default=False)
    is_advertise = models.BooleanField(default=False) # 광고 동의 여부

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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateField()
    order_status = models.CharField(max_length=50)
    shipping_address = models.CharField(max_length=300)
    postal_code = models.CharField(max_length=5)
    recipient = models.CharField(max_length=100)
    recipient_phone_number = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20)

    def __str__(self):
        return str(self.order_id)

# 결제 예정금액 저장
class OrderItem(models.Model):
    orderitem_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('seller.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField() 

    def __str__(self):
        return str(self.orderitem_id)

# paid_amount -> total paid_amount 로 수정
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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey('seller.Product', on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)    