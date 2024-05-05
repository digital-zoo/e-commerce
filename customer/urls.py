from django.urls import path
from customer.views import *
from . import views

app_name='customer'
urlpatterns = [
    #선택된 카테고리 리스트로 이동
    path('<int:category_id>', CategoryList.as_view(),name='category_list'),
    path('cart/<int:pk>/', views.cart, name='cart'), # 카트 상세 페이지 url
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'), # 장바구니 담기 버튼 url
    path('product_detail/<int:product_id>', product_detail, name='product_detail'), # 연희님
    path('cart/delete/<int:user_id>/', views.delete_cart_item, name="delete_cart_item"), # 장바구니 삭제 url
    path('cart/update_quantity/<int:user_id>/', views.update_quantity, name='update_quantity'), # 장바구니 내 수량 변경 url
    path('cart/get_cart_summary/<int:user_id>/', views.get_cart_summary, name='get_cart_summary'), # 수량에 따른 가격 변경 처리 url
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
