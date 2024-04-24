from django.contrib import admin
from .models import Seller,Category,Product,ProductImage

admin.site.register(Seller)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)