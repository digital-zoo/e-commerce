from django.db import models
from customer.models import MyUser
# from django.contrib.auth.models import BaseUserManager
    
class Seller(MyUser):    
    company_name = models.CharField(max_length=255)    
    business_contact = models.CharField(max_length=255,unique=True,null=True)
    registration_number = models.CharField(max_length=255,unique=True)