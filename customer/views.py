from django.shortcuts import render
from django.views.generic import ListView
from seller.models import *
from .models import *
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import date
from datetime import datetime
from django.http import JsonResponse
import json
from django.db import transaction

# Create your views here.
class CategoryList(ListView):
    template_name='home.html'
    paginate_by=2

    #필요한 데이터 가져오기
    def get_queryset(self):
        product_queryset = Product.objects.all()
        category_queryset = Category.objects.all()
        return list(product_queryset) + list(category_queryset)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #category_id인자 받아오기
        category_id = self.kwargs['category_id']
        #선택된 카테고리에 해당하는 상품들만 추출
        category=Category.objects.get(category_id=category_id)
        context['products'] =  Product.objects.filter(category=category)
        context['categories'] = Category.objects.all()
        context['current_category'] = category
        return context
    

def product_detail(request, product_id):
    #user = request.user
    product = Product.objects.get(product_id=product_id)
    product_imgs = ProductImage.objects.filter(product = product)
    #cart, _ = Cart.objects.get_or_create(customer=user)
    #cartitem, _ = CartItem.objects.get_or_create(cart=cart, product=product)
    #cartitem_total_quantity = user.cartitem_set.aggregate(totalcount=Sum('quantity'))['totalcount']
    context = {
        'product':product,
        'product_imgs': product_imgs,
        #'cartitemQuantity':cartitem.quantity,
        #'totalCartitemQuantity':cartitem_total_quantity
    }
    return render(request, 'customer/product_detail.html', context)

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)            
            return redirect('home') # 로그인 성공 후 리다이렉트할 페이지
        else:
            # 실패한 경우, 로그인 페이지에 에러 메시지를 표시할 수 있습니다.
            return HttpResponse('로그인 실패. 다시 시도해주세요.')
    else:
        # GET 요청일 경우 로그인 폼을 보여주는 페이지를 렌더링
        return render(request,"customer/login.html")

def logout_view(request):
    logout(request)
    return redirect("customer:login")

@login_required
def quick_checkout(request):
    if request.method == 'GET': # 페이지 로딩시
        # 구매자 정보 불러오기
        user = request.user
        # 선택한 상품 불러오기
        product_id = request.GET.get('product_id')
        product = Product.objects.get(product_id=product_id)
        # 선택한 상품 수량 불러오기
        quantity = request.GET.get('quantity')
        # 가격 계산하기
        discounted_price = product.price * (1-product.discount_rate)
        final_price = discounted_price * int(quantity)

        context = {
        'user' : user,
        'product': product,
        'quantity': quantity,
        'discounted_price' : discounted_price,
        'final_price' : final_price
        }
        return render(request, 'customer/checkout.html', context)
    
@login_required
@transaction.atomic
def payment(request):
    if request.method == 'POST': # 주문하기 버튼이 눌린 경우
        print("post 호출됨")

        # 선택한 상품 불러오기
        product_id = request.POST.get('product_id')
        # 선택한 상품 수량 불러오기
        quantity = request.POST.get('quantity')

        # 제품 재고 감소 # 동시성처리
        product_udt = Product.objects.select_for_update(nowait=False).get(product_id=product_id)
        if product_udt.stock >= 100: # 재고가 충분할 때 정상처리
            product_udt.stock -= quantity
            product_udt.save()
        else:
            return JsonResponse({'error': '재고부족'}, status=400) # 롤백, 종료
        
        # 구매자 정보 불러오기
        user = request.user
        # 선택한 상품 수량 불러오기
        # quantity = request.POST.get('quantity')
        # 선택한 상품 불러오기
        product = Product.objects.get(product_id=product_id)
        # 배송 정보 불러오기
        shipping_address = request.POST.get('shipping_address')
        shipping_address_detail = request.POST.get('shipping_address_detail')
        postal_code = request.POST.get('postal_code')
        recipient = request.POST.get('recipient')
        recipient_phone_number = request.POST.get('recipient_phone_number')
        payment_method = request.POST.get('payment_method')
        # 결제 가격 불러오기
        # final_price = request.POST.get('paid_amount') # 실제 결제된 금액. 현재는 100원 -> 테스트 완료 후 사용할 금액
        final_price = request.POST.get('final_price') # 실제 상품 가격 -> 테스트 중 DB에 저장될 가격
        # 현재 날짜 가져오기
        today = date.today()

        # 주문서 만들기
        order = Order.objects.create(
                    # order_id = 3,
                    customer = user,
                    order_date = today,
                    order_status = '결제완료',
                    shipping_address = shipping_address + ' ' + shipping_address_detail,
                    postal_code = postal_code,
                    recipient = recipient,
                    recipient_phone_number = recipient_phone_number,
                    payment_method = payment_method
                )
        OrderItem.objects.create(
                    order = order,
                    product=product,
                    quantity=quantity
                )
        Payment.objects.create(
                    order = order,
                    final_price = final_price,
                )       

    # 트랜잭션 시작
    # 주문서 생성 및 주문 메뉴 생성
    # 재고 차감
    # 장바구니 비우기
    # 실제 결제 진행
    # 트랜잭션 커밋
    # 트랜잭션 실패 시 롤백        
        return JsonResponse({'message': 'Order created successfully'}, status=200)

# def decrease_stock(product_id, quantity):
#     try:
#         product = Product.objects.select_for_update(nowait=False).get(product_id=product_id)
#         if product.stock >= quantity: # 재고가 충분할 때 정상처리
#             product.stock -= quantity
#             product.save()
#         else:
#             raise Exception("재고가 부족합니다")
#     except Product.DoesNotExist:
#         raise Exception("해당 상품이 존재하지 않습니다")
    
def order_success(request):
        return render(request, 'customer/order_confirmation.html')

def order_fail(request):
        return render(request, 'customer/order_fail.html')
