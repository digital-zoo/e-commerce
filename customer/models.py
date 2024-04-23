from django.db import models

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)  # 카트ID는 자동으로 생성되는 순차적인 정수
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Customer 테이블과 외래키 관계, 

class CartItem(models.Model):
    cartitem_id = models.AutoField(primary_key=True)  # 카트아이템ID는 자동으로 생성되는 순차적인 정수
    cart_id = models.ForeignKey(Cart, on_delete=models.CASCADE)  # 카트와의 외래키 관계, 카트가 삭제되면 관련된 카트아이템도 삭제
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)  # product와 외래키 관계, 
    quantity = models.IntegerField()  # 수량은 정수형
    