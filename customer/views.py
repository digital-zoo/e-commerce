from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView
from django.db.models import Q
from seller.models import *
from customer.models import *
from django.db.models import Sum, F, FloatField
from django.http import JsonResponse
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
    template_name='customer/product_category.html'
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
        context['current_sorted_by'] = ''
        return context


from django.db.models import Count
class SortedList(ListView):
    template_name='home.html'
        
    model = Product
    context_object_name = 'products'  
        
    def get_queryset(self):
        sorted_by = self.kwargs['sorted_by']
        if sorted_by == 'newest':
            return Product.objects.order_by('-discount_rate')
        elif sorted_by == 'order':
            return Product.objects.annotate(num_orders=Count('orderitem')).order_by('-num_orders')
        elif sorted_by == 'like':
            return Product.objects.annotate(num_likes=Count('like')).order_by('-num_likes')
        else:
            return Product.objects.all()
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_sorted_by'] = self.kwargs['sorted_by']
        return context


class CategorySortedList(ListView):
    template_name='customer/product_category.html'
        
    model = Product
    context_object_name = 'products'  
        
    def get_queryset(self):
        sorted_by = self.kwargs['sorted_by']
        category_id = self.kwargs['category_id']
        #선택된 카테고리에 해당하는 상품들만 추출
        category=Category.objects.get(category_id=category_id)
        products = Product.objects.filter(category=category)
        
        if sorted_by == 'newest':
            return products.order_by('-discount_rate')
        elif sorted_by == 'order':
            return products.annotate(num_orders=Count('orderitem')).order_by('-num_orders')
        elif sorted_by == 'like':
            return products.annotate(num_likes=Count('like')).order_by('-num_likes')
        else:
            return products.all()
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs['category_id']
        #선택된 카테고리에 해당하는 상품들만 추출
        category=Category.objects.get(category_id=category_id)
        context['categories'] = Category.objects.all()
        context['current_sorted_by'] = self.kwargs['sorted_by']
        context['current_category'] = category
        return context



def like_product(request,product_id):
    if request.method == 'POST' and  request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        customer = Customer.objects.all()[1]
        # customer = get_object_or_404(Customer, id=13)
        product = get_object_or_404(Product, pk=product_id)
        
        try:
            # 이미 좋아요를 했는지 확인
            like_instance = Like.objects.get(product=product, customer=customer )
            # 이미 좋아요를 했다면 취소
            like_instance.delete()
            likeTF = False
        except Like.DoesNotExist:
            # 좋아요를 하지 않았다면 추가
            Like.objects.create(product=product, customer=customer)
            likeTF = True
        
        return JsonResponse({'success': True, 'likeTF': likeTF})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    

def search_product(request):
    if request.method == 'POST':

        search_word = request.POST.get('search_word')  # POST 요청으로부터 검색어 가져오기
        if search_word:
            product_list = Product.objects.filter(Q(product_name__icontains=search_word) | Q(description__icontains=search_word)).distinct()
            # 검색 결과를 템플릿에 전달
        else:
            product_list = []
        return render(request, 'customer/search.html', {'products': product_list, 'search_word': search_word})  
# 장바구니 상세 페이지 처리    
def cart(request, pk):
    cart, _ = Cart.objects.get_or_create(customer_id=pk) # 장바구니가 있으면 get, 없으면 create
    cartitem = CartItem.objects.filter(cart_id=cart.cart_id) # 해당 유저의 장바구니에 속한 모든 아이템들
    if cartitem: # 장바구니에 물건이 있는 경우 

        # "item_total"이라는 필드 생성, 해당 필드에는 각 아이뎀의 수량과 가격을 곱한 아이템별 가격 표시 -> 집계 함수를 통해 총 가격 표현
        total_price = CartItem.objects.all().annotate(item_total=F('quantity') * F('product__price')).aggregate(total=Sum('item_total'))['total'] 
        # 할인이 적용된 가격을 표현
        discount_price = CartItem.objects.all().annotate(discounted_price=F('quantity') * F('product__price') * (1 - F('product__discount_rate'))).aggregate(total=Sum('discounted_price', output_field=FloatField()))['total']

        context = {
            'object' : cartitem,
            'total_price' : total_price,
            'discount_price' : total_price - discount_price,
            'final_price' : discount_price,
            
        }
        return render(request, 'customer/cart_list.html', context)
    
    else: # 장바구니에 물건이 없는 경우
        context = {
            'object' : cartitem,
            'total_price' : 0,
            'discount_price' : 0,
            'final_price' : 0,
            
        }
        return render(request, 'customer/cart_list.html', context)

# 장바구기에 아이템 추가하는 메서드
def add_to_cart(request):
    if request.user.is_authenticated: # 로그인한 유저
        user = request.user
        product_id = request.POST['product_id']
        product = Product.objects.get(product_id=product_id)
        
        cart, cart_created = Cart.objects.get_or_create(customer_id=user.id)
        cartitem, caritem_created = CartItem.objects.get_or_create(cart_id=cart.cart_id, product_id=product_id, defaults={'quantity':0})
        cartitem.quantity += int(request.POST['quantity'])
        cartitem.save()
        
        return JsonResponse({'message': 'Item added to cart successfully', 'added': True}, status=200)
    
    # else: # 로그인x 유저
    #     #cart = request.session.get('cart', {})
    #     product_id = request.POST['product_id']
    #     cart = request.session[product_id] = {}
    #     cart[product_id] = cart.get(product_id, 0) + int(request.POST['quantity'])
    #     request.session['test'] = 12
    #     return JsonResponse({'message': 'Item added to cart successfully', 'added': True}, status=200)
# 연희님 코드
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
  
# 장바구니 삭제 버튼
def delete_cart_item(request, user_id):
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(customer_id=user_id)
            CartItem.objects.get(cart_id=cart.cart_id, product_id=int(request.POST['product_id'])).delete()
            cartitem = CartItem.objects.all()
            if cartitem: # 장바구니에 남은 물건이 있는 경우
                total_price = CartItem.objects.all().annotate(item_total=F('quantity') * F('product__price')).aggregate(total=Sum('item_total'))['total']
                final_price = CartItem.objects.all().annotate(discounted_price=F('quantity') * F('product__price') * (1 - F('product__discount_rate'))).aggregate(total=Sum('discounted_price', output_field=FloatField()))['total']
                discount_price = total_price - final_price
                

                return JsonResponse({
                    'success': True, 
                    'total_price' : total_price,
                    'discount_price': discount_price,
                    'final_price': final_price
                    })
            else: # 장바구니에 남은 물건이 없는 경우
                return JsonResponse({
                    'success': True, 
                    'total_price' : 0,
                    'discount_price': 0,
                    'final_price': 0
                    })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
# 장바구니 수량 변경
def update_quantity(request, user_id):
    # 장바구니의 수량을 변경해야함!
    cart = Cart.objects.get(customer_id=user_id)
    cartitem = CartItem.objects.get(cart_id=cart.cart_id, product_id=request.POST['product_id'])
    cartitem.quantity = int(request.POST['quantity']) # 요청한 수량으로 수량 변경
    cartitem.save() # 변경된 내용 저장
    total_price = CartItem.objects.all().annotate(item_total=F('quantity') * F('product__price')).aggregate(total=Sum('item_total'))['total']
    final_price = CartItem.objects.all().annotate(discounted_price=F('quantity') * F('product__price') * (1 - F('product__discount_rate'))).aggregate(total=Sum('discounted_price', output_field=FloatField()))['total']
    discount_price = total_price - final_price
    one_price = cartitem.product.price * (1 - cartitem.product.discount_rate) * cartitem.quantity # 각 아이템별 가격을 표시하기 위한 변수
    return JsonResponse({
        'success' : True,
        'total_price': total_price,
        'discount_price': discount_price,
        'final_price': final_price,
        'one_price' : int(one_price)
    })

# 장바구니 수량 변경에 따른 가격을 처리하기 위한 메서드
def get_cart_summary(request):
    total_price = CartItem.objects.all().annotate(item_total=F('quantity') * F('product__price')).aggregate(total=Sum('item_total'))['total']
    final_price = CartItem.objects.all().annotate(discounted_price=F('quantity') * F('product__price') * (1 - F('product__discount_rate'))).aggregate(total=Sum('discounted_price', output_field=FloatField()))['total']
    discount_price = total_price - final_price 
    return JsonResponse({
        'success' : True,
        'total_price': total_price,
        'discount_price': discount_price,
        'final_price': final_price
    })

# 세션 장바구니
def guest_cart(request):
    # 세션에서 장바구니를 가져옵니다.
    cart = request.session.get('cart', {})

    # 장바구니에 있는 상품들의 정보를 가져와서 템플릿에 전달합니다.
    products = Product.objects.filter(id__in=cart.keys())
    for product in products:
        product.quantity = cart[str(product.id)]
    
    return render(request, 'customer/cart.html', {'products': products})

from django.shortcuts import redirect
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from .forms import SignupForm
from django.views import View
from .models import Customer,Membership
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # 로그인 성공 후 리다이렉트할 페이지. 예를 들어 홈페이지로 리다이렉트
            return redirect('home')
        else:
            # 실패한 경우, 로그인 페이지에 에러 메시지를 표시할 수 있습니다.
            # messages.error(request, '로그인 실패. 다시 시도해주세요.')
            return redirect('customer:login')
    else:
        # GET 요청일 경우 로그인 폼을 보여주는 페이지를 렌더링
        return render(request,"customer/login.html")

def logout_view(request):
    logout(request)
    return redirect("home")

class SignupView(View):
    form_class = SignupForm
    template_name = 'customer/signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer:login")  # 로그인 페이지로 리다이렉트
        return render(request, self.template_name, {'form': form})

#마이페이지 mypage_view
def mypage_view(request):
    return render(request,"customer/mypage.html")

def profile_edit_view(request):
    if request.method == "POST":
        user = request.user 

        new_email = request.POST.get("email")        
        # 현재 사용자를 제외한 다른 사용자가 제출된 이메일을 사용하고 있는지 확인
        if MyUser.objects.filter(~Q(pk=user.pk), email=new_email).exists():
            # 만약 제출된 이메일이 현재 사용자를 제외한 다른 사용자에 의해 이미 사용되고 있다면 오류 메시지를 설정하고 리디렉션
            # messages.error(request, "입력하신 이메일은 이미 사용 중입니다.")
            return redirect('customer:profile_edit')        
        user.email = new_email

        new_phone_number = request.POST.get("phone_number")      
        if MyUser.objects.filter(~Q(pk=user.pk), phone_number=new_phone_number).exists():            
            # messages.error(request, "입력하신 휴대폰 번호는 이미 사용 중입니다.")
            return redirect('customer:profile_edit')        
        user.phone_number = new_phone_number
        
        user.save()        
        
        customer = Customer.objects.get(pk=user.pk)
        customer.customer_name = request.POST.get("customer_name")
        customer.address = request.POST.get("address")
        customer.postal_code = request.POST.get("postal_code")
        customer.save()
        
        # messages.success(request, "프로필이 성공적으로 업데이트되었습니다.")
        return redirect('customer:profile_edit')
    else:
        if not request.user.is_authenticated:
            # 로그인하지 않은 사용자는 로그인 페이지로 리다이렉트
            return redirect('customer:login')

        try:
            # 현재 로그인한 사용자로부터 Customer 정보를 가져옵니다.
            customer = Customer.objects.get(pk=request.user.pk)
        except Customer.DoesNotExist:
            # Customer 정보가 존재하지 않을 경우 처리
            customer = None
        
        try:        
            membership = Membership.objects.get(membership_id=customer.membership_id)
        except Membership.DoesNotExist:        
            membership = None

        context = {
            'grade':membership.grade if membership else "비어있음",
                        
            'customer_name': customer.customer_name if customer else "비어있음",
            'address':customer.address if customer else "비어있음",
            'postal_code':customer.postal_code if customer else "비어있음",                    
        }
        
        return render(request, 'customer/profile_edit.html', context)

def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # 중요: 비밀번호가 변경된 후에도 사용자가 로그아웃되지 않도록 함
            # messages.success(request, "비밀번호 변경 성공")
            return redirect('customer:mypage')
        else:
            # messages.error(request, "비밀번호 변경이 실패하였습니다.다시 시도 해주세요.")
            return redirect('customer:change_password')
    else:
        form = PasswordChangeForm(request.user)
        return render(request, 'customer/change_password.html', {'form': form})
    
@login_required
def delete_customer_view(request):
    if request.method == 'POST' and request.POST['delete_customer?'] == '회원탈퇴':
        # 현재 로그인한 사용자를 삭제합니다.
        user = request.user
        user.delete()
        # messages.success(request, '계정이 성공적으로 삭제되었습니다.')
        return redirect('home')
    else:
        # messages.error(request, '계정이 삭제가 실패했습니다.')
        return render(request, 'customer/delete_customer.html')


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
def save_order(request):
    if request.method == 'POST': # 주문하기 버튼이 눌린 경우
        print("post 호출됨")
        # 선택한 상품 id 불러오기
        product_id = request.POST.get('product_id')
        # 선택한 상품 수량 불러오기
        quantity = request.POST.get('quantity')

        # 제품 재고 확인
        product_udt = Product.objects.get(product_id=product_id)
        if product_udt.stock >= int(quantity): # 재고가 충분한지 확인
            pass
        else:
            return JsonResponse({'success': False, 'message': '현재 상품의 재고가 충분하지 않습니다'}) # 롤백(이 단계에선 할 것 없음), 종료
        
        # 구매자 정보 불러오기
        user = request.user
        # 선택한 상품 불러오기
        product = Product.objects.get(product_id=product_id)
        # 배송 정보 불러오기
        shipping_address = request.POST.get('shipping_address')
        shipping_address_detail = request.POST.get('shipping_address_detail')
        postal_code = request.POST.get('postal_code')
        recipient = request.POST.get('recipient')
        recipient_phone_number = request.POST.get('recipient_phone_number')
        # 결제 정보 불러오기
        payment_method = request.POST.get('payment_method')
        # # final_price = request.POST.get('paid_amount') # 실제 결제된 금액. 현재는 100원 -> 테스트 완료 후 사용할 금액
        # final_price = request.POST.get('final_price') # 실제 상품 가격 -> 테스트 중 DB에 저장될 가격
        # 현재 날짜 가져오기
        today = date.today()

        # 주문서 만들기
        order = Order.objects.create(
                    customer = user,
                    order_date = today,
                    order_status = '주문중',
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

    # 트랜잭션 시작
    # 주문서 생성 및 주문 메뉴 생성
    # 재고 차감
    # 장바구니 비우기
    # 실제 결제 진행
    # 트랜잭션 커밋
    # 트랜잭션 실패 시 롤백        
        #return JsonResponse({'message': 'Order created successfully', 'order_id': order.order_id}, status=200)
        return JsonResponse({'success': True, 'message': '결제가 완료되어야 구매가 완료됩니다.', 'order_id': order.order_id}) # 메세지는 사용 안됨

@login_required
@transaction.atomic
def save_payment(request):
    if request.method == 'POST': # 주문하기 버튼이 눌린 경우
        print("post 호출됨(save_payment)")
        # 선택한 상품 id 불러오기
        product_id = request.POST.get('product_id')
        # 선택한 상품 수량 불러오기
        quantity = request.POST.get('quantity')

        order_id = request.POST.get('order_id')
        # 결제가 된 주문 가져오기
        order = Order.objects.get(order_id=order_id)

        # 제품 재고 변경 # 동시성처리 # 결제 과정이 오래 걸리면 여기서 문제 발생
        product_udt = Product.objects.select_for_update(nowait=False).get(product_id=product_id)
        if product_udt.stock >= int(quantity): # 재고가 충분할 때 정상처리
            product_udt.stock -= int(quantity)
            #여기에 하단의 과정을 다 넣어야 하나??? 아마도??? 아님. 빨리 처리할 수록 좋음 어제까지 섹렉트호업데이트가 홀드 되는지 찾아보기 세이브까지 아니면 트랜젝션 모두
            product_udt.save() #save가 트랜젝션에 영향 안주는게 맞는지 확인 필요--> 영향이 가는 듯 -> 안감!!!

            # order.order_status = '오징어오징어' # 아래서 핸들 안된 오류 발생하니깐 적용 안됨
            # order.save()
        else:
            # 결제 취소..는 돌아가서 
            # 순서가 위랑 결제 취소랑 안 맞지만 여기서 오더 주문취소 처리->뒤에서 가능하면 환불이후 환불처리?
            order.order_status = '환불처리중'
            order.save() # 환불처리로 바뀜 -> 지금 트렌젝션 처리상 여기서 끊기면 안되는데..? ㅇㄴ
            return JsonResponse({'success': False, 'message': '현재 상품의 재고가 충분하지 않습니다. 환불을 도와드리겠습니다.'}) # 롤백(이 단계에선 할 것 없음)아님!! 핸들된 오류, 종료

        order.order_status = '결제완료'
        order.save()

        imp_uid = request.POST.get('imp_uid')
        merchant_uid = request.POST.get('merchant_uid')
        paid_amount = request.POST.get('paid_amount')

        # #DB 백업 -> DB에 Payment 테이블 생성 후 사용가능
        # Payment.objects.create(
        #             order = order,
        #             final_price = paid_amount, # 필드 이름 paid_amount으로 바꾸기
        #             #imp_uid, merchant_uid 필드 생성 하고 넣기
        #         )
        return JsonResponse({'success': True, 'message': 'Payment created successfully'}) # 메시지는 안쓰임

def order_success(request):
        # 상품이랑 결제 정보보여주기
        return render(request, 'customer/order_confirmation.html')

def order_fail(request):
    if request.method == 'POST':
        order_status = request.POST.get('order_status')
        order_id = request.POST.get('order_id')

        order = Order.objects.get(order_id=order_id)
        order.order_status = order_status
        order.save()

        context={
            'message' : '클라이언트 메세지 받아올예정',
            }

        #return JsonResponse({'message': '히히히ㅣ'})
        return render(request, 'customer/order_fail.html', context)


        # context={
        #     'order_id' : order_id,
        #     'order_status' : order_status
        #     }
        
        # return render(request, 'customer/order_fail.html', context)
    
    if request.method == 'GET':
        context={
            'message' : '결제과정에서 문제가 생겼습니다.',
            }
        return render(request, 'customer/order_fail.html', context)
