import json
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
    user = request.user
    product = Product.objects.get(product_id=product_id)
    #cart, _ = Cart.objects.get_or_create(customer=user)
    #cartitem, _ = CartItem.objects.get_or_create(cart=cart, product=product)
    #cartitem_total_quantity = user.cartitem_set.aggregate(totalcount=Sum('quantity'))['totalcount']
    context = {
        'object':product,
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
    
# @login_required
# def payment(request):
#     if request.method == 'POST': # 주문하기 버튼이 눌린 경우
#         # 구매자 정보 불러오기
#         user = request.user
#         # 선택한 상품 수량 불러오기
#         quantity = request.POST.get('quantity')
#         # 선택한 상품 불러오기
#         product_id = request.POST.get('product_id')
#         product = Product.objects.get(product_id=product_id)
#         # 가격 계산하기
#         # discounted_price = product.price * (1-product.discount_rate)
#         # final_price = discounted_price * int(quantity)
#         # 배송 정보 불러오기
#         shipping_address = request.POST.get('shipping_address')
#         shipping_address_detail = request.POST.get('shipping_address_detail')
#         postal_code = request.POST.get('postal_code')
#         recipient = request.POST.get('recipient')
#         recipient_phone_number = request.POST.get('recipient_phone_number')
#         payment_method = request.POST.get('payment_method')

#         # 현재 날짜 가져오기
#         today = date.today()

#         # 주문서 만들기
#         order = Order.objects.create(
#                     # order_id = 3,
#                     customer = user,
#                     order_date = today,
#                     order_status = '주문생성',
#                     shipping_address = shipping_address + ' ' + shipping_address_detail,
#                     postal_code = postal_code,
#                     recipient = recipient,
#                     recipient_phone_number = recipient_phone_number,
#                     payment_method = payment_method
#                 )
#         OrderItem.objects.create(
#                     order = order,
#                     product=product,
#                     quantity=quantity
#                 )
        
#         # product 테이블에서 재고 줄여야 함. 결제 완료 후
#         # db에서 말고 동시성처리?
#         # 결제 될 때까지 다시 한번 재고 확인

#         # 실제 결제 모듈

#         # 트랜잭션 시작
#         # 주문서 생성 및 주문 메뉴 생성
#         # 재고 차감 ⚠
#         # 장바구니 비우기
#         # 실제 결제 진행
#         # 트랜잭션 커밋
#         # 트랜잭션 실패 시 롤백
        
#         # IMP = window.IMP
#         # code = "imp26236276"  #v가맹점 식별코드
#         # IMP.init(code)

#         # #결제요청
#         # IMP.request_pay({
#         #     // name과 amount만 있어도 결제 진행가능
#         #     pg : 'html5_inicis', // 이니시스 결제창 일반/정기결제
#         #     pay_method : 'card', // 신용카드 
#         #     merchant_uid : 'merchant_' + new Date().getTime(),
#         #     name : '주문명:결제테스트',
#         #     amount : {{ final_price|floatformat:"0" }},
#         #     buyer_email : 'iamport@siot.do',
#         #     buyer_name : '구매자이름',
#         #     buyer_tel : '010-1234-5678',
#         #     buyer_addr : '서울특별시 강남구 삼성동',
#         #     buyer_postcode : '123-456',
#         #     m_redirect_url : '{% url "customer:quick_checkout" %}'
#         # }, function(rsp) {
#         #     if ( rsp.success ) {
#         #         var msg = '결제가 완료되었습니다.';
#         #         msg += '고유ID : ' + rsp.imp_uid;
#         #         msg += '상점 거래ID : ' + rsp.merchant_uid;
#         #         msg += '결제 금액 : ' + rsp.paid_amount;
#         #         msg += '카드 승인번호 : ' + rsp.apply_num;
#         #     }
#         #     else {
#         #         var msg = '결제에 실패하였습니다. 에러내용 : ' + rsp.error_msg
#         #     }
#         #     alert(msg);
#         # })

#         #return order_success(request)
#         return render(request, 'customer/order_confirmation.html')

@login_required
def payment(request):
    if request.method == 'POST': # 주문하기 버튼이 눌린 경우
        # 전달된 JSON 데이터 파싱
        payment_info = json.loads(request.body)

        # 구매자 정보 불러오기
        user = request.user
        # 선택한 상품 수량 불러오기
        quantity = request.POST.get('quantity')
        # 선택한 상품 불러오기
        product_id = request.POST.get('product_id')
        product = Product.objects.get(product_id=product_id)
        # 가격 계산하기
        # discounted_price = product.price * (1-product.discount_rate)
        # final_price = discounted_price * int(quantity)
        # 배송 정보 불러오기
        shipping_address = request.POST.get('shipping_address')
        shipping_address_detail = request.POST.get('shipping_address_detail')
        postal_code = request.POST.get('postal_code')
        recipient = request.POST.get('recipient')
        recipient_phone_number = request.POST.get('recipient_phone_number')
        payment_method = request.POST.get('payment_method')

        # 현재 날짜 가져오기
        today = date.today()

        # 주문서 만들기
        order = Order.objects.create(
                    # order_id = 3,
                    customer = user,
                    order_date = today,
                    order_status = '주문생성',
                    shipping_address = payment_info['buyer_addr'],
                    postal_code = payment_info['buyer_postcode'],
                    recipient = payment_info['buyer_name'],
                    recipient_phone_number = payment_info['buyer_tel'],
                    payment_method = payment_info['pay_method']
                )
        OrderItem.objects.create(
                    order = order,
                    product=product,
                    quantity=quantity
                )
    

        # 응답 데이터 반환
        return JsonResponse({'message': '결제 정보 저장 완료'})
    else:
        return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=405)
    
def order_success(request):
        return render(request, 'customer/order_confirmation.html')





