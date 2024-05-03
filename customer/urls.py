from django.urls import path
from customer.views import *

app_name='customer'
urlpatterns = [
    #선택된 카테고리 리스트로 이동
    path('<int:category_id>/', CategoryList.as_view(),name='category_list'),
    path('<str:sorted_by>/', SortedList.as_view() ,name='sorted_list'),
    path('<int:category_id>/<str:sorted_by>/', CategorySortedList.as_view() ,name='category_sorted_list'),
    path('like/<int:product_id>/', like_product, name='like_product'),
    path('product/search/', search_product, name='search_product'),
]
