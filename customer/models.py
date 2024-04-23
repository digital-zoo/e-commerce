from django.db import models

# Create your models here.
class Membership(models.Model):
    membership_id = models.IntegerField(primary_key=True)
    grade = models.CharField(max_length=255,unique=True)

class Customer(models.Model):    
    customer_id = models.CharField(primary_key=True,max_length=255)
    membership_id = models.ForeignKey(Membership,on_delete=models.DO_NOTHING)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    customer_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255,unique=True)
    address = models.CharField(max_length=255,null=True)
    postal_code = models.CharField(max_length=255,null=True)
    sns = models.BooleanField()
