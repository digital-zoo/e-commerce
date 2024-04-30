from django.urls import path
from seller.views import *

app_name='seller'
urlpatterns = [    
    path('login/', seller_login_view, name='seller_login'),
    path('logout/', seller_logout_view, name='seller_logout'),
    path('signup/', seller_signup_view, name='seller_signup'),
]