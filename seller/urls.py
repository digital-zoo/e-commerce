from django.urls import path
from seller.views import *

app_name='seller'
urlpatterns = [    
    path('login/', seller_login_view, name='seller_login'),
    path('logout/', seller_logout_view, name='seller_logout'),
    path('signup/', seller_signup_view, name='seller_signup'),
    path('mypage/', seller_mypage_view, name='seller_mypage'),    
    path('mypage/change_password', seller_change_password_view, name='seller_change_password'),    
    path('mypage/profile_edit/', seller_profile_edit_view, name='seller_profile_edit'),
    path('mypage/delete_seller/', delete_seller_view, name='delete_seller_view'), 
]