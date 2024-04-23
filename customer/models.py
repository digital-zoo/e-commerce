from django.db import models

class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)  # 카트ID는 자동으로 생성되는 순차적인 정수
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Customer 테이블과 외래키 관계, 

class CartItem(models.Model):
    cartitem_id = models.AutoField(primary_key=True)  # 카트아이템ID는 자동으로 생성되는 순차적인 정수
    cart_id = models.ForeignKey(Cart, on_delete=models.CASCADE)  # 카트와의 외래키 관계, 카트가 삭제되면 관련된 카트아이템도 삭제
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)  # product와 외래키 관계, 
    quantity = models.IntegerField()  # 수량은 정수형
    
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

class Order(models.Model):
    order_id = models.AutoField(primary_key=True) 
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateField()
    order_status = models.CharField(max_length=50)
    shipping_address = models.CharField(max_length=300)
    postal_code = models.CharField(max_length=5)
    recipient = models.CharField(max_length=100)
    recipient_phone_number = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20)

    def __str__(self):
        return str(self.order_id)

class OrderItem(models.Model):
    orderitem_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField() 

    def __str__(self):
        return str(self.orderitem_id)

class Like(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} liked {self.product.name}"
    
    class Meta:
        ordering = ['-created_at']