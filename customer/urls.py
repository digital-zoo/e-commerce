from django.urls import path
from customer.views import *

app_name='customer'
urlpatterns = [
    #선택된 카테고리 리스트로 이동
    path('<int:category_id>', CategoryList.as_view(),name='category_list'),
    path('product_detail/<int:product_id>', product_detail, name='product_detail'),
    path('quick_checkout/', quick_checkout, name='quick_checkout'),
    path('simulate_login/', simulate_login, name='simulate_login'),
    path('s_logout/', s_logout, name='s_logout'),
]
