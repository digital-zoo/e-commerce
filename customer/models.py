from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class MyModel(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=255, unique=True)
    is_staff = models.BooleanField(default=False)  # 관리자 사이트 접근 권한

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email'] #superusercreate할 때 email 필요

    def __str__(self):
        return self.username

class Membership(models.Model):
    membership_id = models.IntegerField(primary_key=True)
    grade = models.CharField(max_length=255, unique=True)

class CustomerManager(BaseUserManager):
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
    
class Customer(MyModel):    
    membership = models.ForeignKey(Membership, on_delete=models.DO_NOTHING)    
    customer_name = models.CharField(max_length=255)    
    address = models.CharField(max_length=255, null=True)
    postal_code = models.CharField(max_length=255, null=True)
    is_snsid = models.BooleanField()

    objects = CustomerManager()