from django.contrib import admin
from .models import Customer,Cart,CartItem,Order,OrderItem,Like,Membership

admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Like)
admin.site.register(Membership)