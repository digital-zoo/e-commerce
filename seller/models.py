from django.db import models
from customer.models import MyModel
from django.contrib.auth.models import BaseUserManager

class SellerManager(BaseUserManager):
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
    
class Seller(MyModel):    
    company_name = models.CharField(max_length=255)    
    business_contact = models.CharField(max_length=255,unique=True,null=True)
    registration_number = models.CharField(max_length=255,unique=True) 

    objects = SellerManager()