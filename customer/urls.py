from django.urls import path
from customer.views import *
from . import views

app_name='customer'
urlpatterns = [
    #선택된 카테고리 리스트로 이동
    path('<int:category_id>', CategoryList.as_view(),name='category_list'),
    path('cart/<int:pk>/', views.cart, name='cart'),
    path('detail/<int:pk>', views.product_detail, name='product_detail'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
]
