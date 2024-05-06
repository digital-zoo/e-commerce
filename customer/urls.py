from django.urls import path
from customer.views import *

app_name='customer'
urlpatterns = [
    #선택된 카테고리 리스트로 이동
    path('<int:category_id>', CategoryList.as_view(),name='category_list'),
    path('product_detail/<int:product_id>', product_detail, name='product_detail'),
    path('quick_checkout/', quick_checkout, name='quick_checkout'),
    path('payment/', payment, name='payment'),
    path('order_success/', order_success, name='order_success'),
    path('order_fail/', order_fail, name='order_fail'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
