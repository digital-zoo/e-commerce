from django.urls import path
from seller.views import *
from django.contrib import admin
from django.urls import path,include
from . import views

app_name='seller'
urlpatterns = [    
    path('login/', seller_login_view, name='seller_login'),
    path('logout/', seller_logout_view, name='seller_logout'),
    path('signup/', seller_signup_view, name='seller_signup'),
    path('mypage/', seller_mypage_view, name='seller_mypage'),    
    path('mypage/change_password', seller_change_password_view, name='seller_change_password'),    
    path('mypage/profile_edit/', seller_profile_edit_view, name='seller_profile_edit'),
    path('mypage/delete_seller/', delete_seller_view, name='delete_seller'), 
    path('', views.seller_index, name='seller_index' ),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_image/<int:product_id>/', views.edit_product, name='delete_image'),
    path('order_manage/', views.order_manage, name='order_manage'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),

]



