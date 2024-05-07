from django.urls import path
from customer.views import *
from . import views

app_name='customer'
urlpatterns = [
    path('cart/<int:pk>/', views.cart, name='cart'), # 카트 상세 페이지 url
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'), # 장바구니 담기 버튼 url
    path('product_detail/<int:product_id>', product_detail, name='product_detail'), # 연희님
    path('cart/delete/<int:user_id>/', views.delete_cart_item, name="delete_cart_item"), # 장바구니 삭제 url
    path('cart/update_quantity/<int:user_id>/', views.update_quantity, name='update_quantity'), # 장바구니 내 수량 변경 url
    path('cart/get_cart_summary/<int:user_id>/', views.get_cart_summary, name='get_cart_summary'), # 수량에 따른 가격 변경 처리 url
    path('cart/guest/', views.guest_cart, name='guest_cart'), # 비회원 장바구니 url

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('signup/', SignupView.as_view(), name='signup'),
    path('mypage/', mypage_view, name='mypage'),    
    path('mypage/change_password', change_password_view, name='change_password'),    
    path('mypage/profile_edit/', profile_edit_view, name='profile_edit'),
    path('mypage/delete_customer/', delete_customer_view, name='delete_customer'),   

    path('<int:category_id>/', CategoryList.as_view(),name='category_list'),#선택된 카테고리 보기
    path('<str:sorted_by>/', SortedList.as_view() ,name='sorted_list'),#기준에 따라 정렬
    path('<int:category_id>/<str:sorted_by>/', CategorySortedList.as_view() ,name='category_sorted_list'),#선택된 카테고리에서 기준에 따라 정렬
    path('like/<int:product_id>/', like_product, name='like_product'),#좋아요
    path('product/search/', search_product, name='search_product'),#검색
]
