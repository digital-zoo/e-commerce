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
from django.http import JsonResponse
from django.db import transaction
import json
import requests
import os
from dotenv import load_dotenv

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
        customer = request.user
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

################################################## 장바구니

# 장바구니 상세 페이지 처리    
def cart(request, pk):
    cart, _ = Cart.objects.get_or_create(customer_id=pk) # 장바구니가 있으면 get, 없으면 create
    cartitem = CartItem.objects.filter(cart_id=cart.cart_id) # 해당 유저의 장바구니에 속한 모든 아이템들
    if cartitem: # 장바구니에 물건이 있는 경우 
        # "item_total"이라는 필드 생성, 해당 필드에는 각 아이뎀의 수량과 가격을 곱한 아이템별 가격 표시 -> 집계 함수를 통해 총 가격 표현
        total_price = cartitem.annotate(item_total=F('quantity') * F('product__price')).aggregate(total=Sum('item_total'))['total'] 
        # 할인이 적용된 가격을 표현
        discount_price = cartitem.annotate(discounted_price=F('quantity') * F('product__price') * (1 - F('product__discount_rate'))).aggregate(total=Sum('discounted_price', output_field=FloatField()))['total']

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

from .forms import CartItemForm # 폼을 활용한 데이터 유효성 검사
from datetime import datetime, timedelta

def add_to_cart(request):
    if request.user.is_authenticated: # 로그인 유저 장바구니 추가
        user = request.user
        product_id = request.POST.get('product_id')

        form = CartItemForm(request.POST) # 클라이언트에서 전송한 POST 데이터를 생성한 CartItemForm에 바인딩
        if form.is_valid(): # 해당 인스턴스가 유효하다면 즉, validators 매개변수에서 지정한 검사를 통과했다면
            quantity = form.cleaned_data['quantity']
            product = Product.objects.get(product_id=product_id)
            cart, cart_created = Cart.objects.get_or_create(customer_id=user.id)
            cartitem, caritem_created = CartItem.objects.get_or_create(cart_id=cart.cart_id, product_id=product_id, defaults={'quantity': 0})
            cartitem.quantity += quantity
            cartitem.save()

            return JsonResponse({'message': 'Item added to cart successfully', 'added': True}, status=200)
        else: # 통과하지 못했다면 즉, 1 이하의 갯수를 클라이언트에서 보냈다면
            return JsonResponse({'message': form.errors['quantity'][0]}, status=400)
    else: # 비로그인 유저 장바구니 추가
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        if request.COOKIES.get(product_id):
            previous_quantity = int(request.COOKIES[product_id])
            request.COOKIES[product_id] = previous_quantity + quantity
        else:
            request.COOKIES[product_id] = quantity
        # # 쿠키에 저장된 기존 장바구니 데이터 가져오기
        # cart = request.COOKIES.get('cart', '')
        
        # # 장바구니 데이터 업데이트
        # if cart:
        #     cart += f"|{product_id}:{quantity}"
        # else:
        #     cart = f"{product_id}:{quantity}"

        response = JsonResponse({'message': 'Item added to cart successfully', 'added': True}, status=200)
        # 장바구니 데이터를 쿠키에 저장
        max_age = 365 * 24 * 60 * 60  # 1년
        expires = datetime.strftime(datetime.utcnow() + timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie(product_id, request.COOKIES[product_id], max_age=max_age, expires=expires)

        return response
# def add_to_cart(request):
#     if request.user.is_authenticated:
#         user = request.user
#         product_id = request.POST.get('product_id')
#         quantity = request.POST.get('quantity')

#         # 수량 값 유효성 검사 try-except 구문 사용
#         try:
#             quantity = int(quantity)
#             if quantity < 1:
#                 return JsonResponse({'message': '유효하지 않은 수량입니다.'}, status=400)
#         except ValueError:
#             return JsonResponse({'message': '유효하지 않은 수량입니다.'}, status=400)
        
#         # # 수량 값 유효성 검사 단순 if 문 사용
#         # if not quantity_str.isdigit() or int(quantity_str) < 1:
#         #     return JsonResponse({'message': '유효하지 않은 수량입니다.'}, status=400)

#         product = Product.objects.get(product_id=product_id)
#         cart, cart_created = Cart.objects.get_or_create(customer_id=user.id)
#         cartitem, caritem_created = CartItem.objects.get_or_create(cart_id=cart.cart_id, product_id=product_id, defaults={'quantity': 0})
#         cartitem.quantity += quantity
#         cartitem.save()

#         return JsonResponse({'message': 'Item added to cart successfully', 'added': True}, status=200)



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
            cartitem = CartItem.objects.filter(cart_id=cart.cart_id)

            if cartitem: # 장바구니에 남은 물건이 있는 경우
                total_price = cartitem.annotate(item_total=F('quantity') * F('product__price')).aggregate(total=Sum('item_total'))['total']
                final_price = cartitem.annotate(discounted_price=F('quantity') * F('product__price') * (1 - F('product__discount_rate'))).aggregate(total=Sum('discounted_price', output_field=FloatField()))['total']
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
    cart = Cart.objects.get(customer_id=user_id)
    cartitem = CartItem.objects.get(cart_id=cart.cart_id, product_id=request.POST['product_id'])
    cartitem.quantity = int(request.POST['quantity']) # 요청한 수량으로 수량 변경
    cartitem.save() # 변경된 내용 저장
    one_price = cartitem.product.price * (1 - cartitem.product.discount_rate) * cartitem.quantity # 각 아이템별 가격을 표시하기 위한 변수
    cartitem = CartItem.objects.filter(cart_id=cart.cart_id)
    total_price = cartitem.annotate(item_total=F('quantity') * F('product__price')).aggregate(total=Sum('item_total'))['total']
    final_price = cartitem.annotate(discounted_price=F('quantity') * F('product__price') * (1 - F('product__discount_rate'))).aggregate(total=Sum('discounted_price', output_field=FloatField()))['total']
    discount_price = total_price - final_price
    
    
    return JsonResponse({
        'success' : True,
        'total_price': total_price,
        'discount_price': discount_price,
        'final_price': final_price,
        'one_price' : int(one_price)
    })

# # 장바구니 수량 변경에 따른 가격을 처리하기 위한 메서드
# def get_cart_summary(request):
#     total_price = CartItem.objects.all().annotate(item_total=F('quantity') * F('product__price')).aggregate(total=Sum('item_total'))['total']
#     final_price = CartItem.objects.all().annotate(discounted_price=F('quantity') * F('product__price') * (1 - F('product__discount_rate'))).aggregate(total=Sum('discounted_price', output_field=FloatField()))['total']
#     discount_price = total_price - final_price 
    
#     return JsonResponse({
#         'success' : True,
#         'total_price': total_price,
#         'discount_price': discount_price,
#         'final_price': final_price
#     })

########################################## 세션 장바구니
from collections import defaultdict

def guest_cart(request):
   # 쿠키에서 장바구니 데이터 가져오기
   cart_data = request.COOKIES

   # 장바구니 데이터 파싱
   cart_items = defaultdict(int)
   for key, value in cart_data.items():
       if key != 'csrftoken':
           product_id, quantity = int(key), int(value)
           cart_items[product_id] += quantity

   # 장바구니 항목 리스트 생성
   cart_item_list = []
   for product_id, quantity in cart_items.items():
       try:
           product = Product.objects.get(product_id=product_id)
           cart_item_list.append({
               'product_id': product_id,
               'product': product,
               'quantity': quantity,
               'total_price': product.price * quantity,
               'final_price' : (1 - product.discount_rate) * product.price * quantity,
               'discount_price' : product.discount_rate * product.price * quantity
           })
       except Product.DoesNotExist:
           pass

   # 컨텍스트 딕셔너리 준비
   context = {
       'object': cart_item_list,
       'total_price': sum(item['total_price'] for item in cart_item_list),
       'discount_price': sum(item['product'].discount_rate * item['total_price'] for item in cart_item_list),
       'final_price': sum(item['total_price'] * (1 - item['product'].discount_rate) for item in cart_item_list)
   }

   return render(request, 'customer/guest_cart.html', context)

def delete_guest_cart_item(request):
    if request.method == 'POST':
        try:
            cart_data = request.COOKIES
            delete_product_id = request.POST.get('product_id')

            if delete_product_id in cart_data:
                del cart_data[delete_product_id]

            has_numeric_key = False
            for key in cart_data.keys():
                if key != 'csrftoken' and key.isdigit():
                    has_numeric_key = True
                    break
            
            if has_numeric_key: # 남은 물건이 있는 경우

                # 장바구니 데이터 파싱
                cart_items = defaultdict(int)
                for key, value in cart_data.items():
                    if key != 'csrftoken':
                        product_id, quantity = int(key), int(value)
                        cart_items[product_id] += quantity

                # 장바구니 항목 리스트 생성
                cart_item_list = []
                for product_id, quantity in cart_items.items():
                    try:
                        product = Product.objects.get(product_id=product_id)
                        cart_item_list.append({
                            'product_id': product_id,
                            'product': product,
                            'quantity': quantity,
                            'total_price': product.price * quantity,
                            'final_price' : (1 - product.discount_rate) * product.price * quantity,
                            'discount_price' : product.discount_rate * product.price * quantity
                        })
                    except Product.DoesNotExist:
                        pass
                
                response = JsonResponse({
                    'success': True, 
                    'total_price': sum(item['total_price'] for item in cart_item_list),
                    'discount_price': sum(item['product'].discount_rate * item['total_price'] for item in cart_item_list),
                    'final_price': sum(item['total_price'] * (1 - item['product'].discount_rate) for item in cart_item_list)
                    })
                response.delete_cookie(str(delete_product_id))

                return response
            
            else: # 삭제 후 남은 물건이 없는 경우
                response = JsonResponse({'success': True, 'total_price': 0, 'discount_price': 0, 'final_price': 0})
                response.delete_cookie(product_id)
                return response
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
def update_guest_cart_quantity(request):
    update_product_id = request.POST['product_id']
    update_quantity = request.POST['quantity']

    if update_product_id in request.COOKIES:
        request.COOKIES[update_product_id] = update_quantity

    cart_data = request.COOKIES
    # 장바구니 데이터 파싱
    cart_items = defaultdict(int)
    for key, value in cart_data.items():
        if key != 'csrftoken':
            product_id, quantity = int(key), int(value)
            cart_items[product_id] += quantity

    # 장바구니 항목 리스트 생성
    cart_item_list = []
    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(product_id=product_id)
            cart_item_list.append({
                'product_id': product_id,
                'product': product,
                'quantity': quantity,
                'total_price': product.price * quantity,
                'final_price' : (1 - product.discount_rate) * product.price * quantity,
                'discount_price' : product.discount_rate * product.price * quantity
            })
        except Product.DoesNotExist:
            pass
    
    response = JsonResponse({
        'success': True, 
        'total_price': sum(item['total_price'] for item in cart_item_list),
        'discount_price': int(sum(item['product'].discount_rate * item['total_price'] for item in cart_item_list)),
        'final_price': sum(item['total_price'] * (1 - item['product'].discount_rate) for item in cart_item_list),
        'one_price' : [{'product_id': item['product_id'], 'price': item['product'].price} for item in cart_item_list]
        })
    for item in cart_item_list:
        response.set_cookie(str(item['product_id']), str(item['quantity']))

    return response

############################################################################

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
        return redirect('customer:mypage')
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
        return redirect('customer:login')
    else:
        # messages.error(request, '계정이 삭제가 실패했습니다.')
        return render(request, 'customer/delete_customer.html')


    return redirect("customer:login")

# 바로결제하기
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
        original_final_price = product.price * int(quantity)
        saved_price = original_final_price - final_price
        # 구매자 배송지 정보 불러오기
        shipping_addresses = ShippingAddress.objects.filter(customer=user)

        context = {
        'user' : user,
        'product': product,
        'quantity': quantity,
        'discounted_price' : discounted_price,
        'final_price' : final_price,
        'original_final_price' : original_final_price,
        'saved_price' : saved_price,
        'shipping_addresses' : shipping_addresses,
        }
        return render(request, 'customer/checkout.html', context)
    
@login_required
@transaction.atomic
def save_order(request):
    if request.method == 'POST': # 주문하기 버튼이 눌린 경우
        # 선택한 상품 id 불러오기
        product_id = request.POST.get('product_id')
        # 선택한 상품 수량 불러오기
        quantity = request.POST.get('quantity')

        # 제품 재고 확인
        product_udt = Product.objects.get(product_id=product_id)
        if product_udt.stock >= int(quantity): # 재고가 충분한지 확인
            pass
        else:
            return JsonResponse({'success': False, 'message': '현재 상품의 재고가 충분하지 않습니다'})
        
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
        # 입력한 주소 배송지 목록에 저장하기
        shipping_address = ShippingAddress.objects.create(
                    customer = user,
                    shipping_address = shipping_address + ' ' + shipping_address_detail,
                    postal_code = postal_code,
                    recipient = recipient,
                    recipient_phone_number = recipient_phone_number
                )
        
        return JsonResponse({'success': True, 'message': '결제가 완료되어야 구매가 완료됩니다.', 'order_id': order.order_id}) # 메세지는 사용 안됨

@login_required
@transaction.atomic
def save_payment(request):
    if request.method == 'POST': # 주문하기 버튼이 눌린 경우
        # 선택한 상품 id 불러오기
        product_id = request.POST.get('product_id')
        # 선택한 상품 수량 불러오기
        quantity = request.POST.get('quantity')
        # 결제가 된 주문 가져오기
        order_id = request.POST.get('order_id')
        order = Order.objects.get(order_id=order_id)

        # 제품 재고 변경 # 동시성처리
        product_udt = Product.objects.select_for_update(nowait=False).get(product_id=product_id)
        if product_udt.stock >= int(quantity): # 재고가 충분할 때 정상처리
            product_udt.stock -= int(quantity)
            product_udt.save()
        else:
            # 재고 부족
            order.order_status = '환불대기'
            order.save()
            return JsonResponse({'success': False, 'message': '현재 상품의 재고가 충분하지 않습니다. 영업일 2일 이내로 환불을 도와드리겠습니다.'}) 

        order.order_status = '결제완료'
        order.save()

        imp_uid = request.POST.get('imp_uid')
        merchant_uid = request.POST.get('merchant_uid')
        # paid_amount = request.POST.get('paid_amount') # 실제로 결제된 금액(현재 100원)
        final_price_str = request.POST.get('final_price') # 결제 금액
        paid_amount = int(float(final_price_str))  # 숫자로 변환

        # 결제 내역 저장
        Payment.objects.create(
                    order = order,
                    paid_amount = paid_amount, 
                    imp_uid = imp_uid, 
                    merchant_uid = merchant_uid
                )
        
        return JsonResponse({'success': True, 'message': 'Payment created successfully', 'order_id': order.order_id}) # 메시지는 안쓰임

# 장바구니 결제하기
@login_required
def cart_checkout(request):
    if request.method == 'GET': # 페이지 로딩시
        # 구매자 정보 불러오기
        user = request.user
        # 카트 불러오기
        cart = Cart.objects.get(customer=user)
        # 카트 아이템 불러오기
        cart_items = CartItem.objects.filter(cart=cart)
        # 구매자 배송지 정보 불러오기
        shipping_addresses = ShippingAddress.objects.filter(customer=user)

        # 각 카트 아이템의 가격 정보를 계산하여 리스트에 저장
        cart_items_info = []
        total_final_price = 0
        total_original_final_price = 0
        for item in cart_items:
            # 상품 하나의 할인된 가격
            discounted_price = item.product.price * (1 - item.product.discount_rate)
            # 할인된 해당 상품의, 상품 개수에 따른 총 가격
            final_price = discounted_price * item.quantity
            # 할인 되지 않은 해당 상품의, 상품 개수에 따른 총 가격 
            original_final_price = item.product.price * item.quantity
            cart_items_info.append({
                'product': item.product,
                'quantity': item.quantity,
                'discounted_price': discounted_price,
                'final_price': final_price,
            })
            total_final_price += final_price
            total_original_final_price += original_final_price
        total_saved_price = total_original_final_price - total_final_price

        context = {
            'user': user,
            'cart_items': cart_items_info,
            'total_final_price': total_final_price,
            'total_original_final_price': total_original_final_price,
            'total_saved_price': total_saved_price,
            'shipping_addresses' : shipping_addresses,
        }
        return render(request, 'customer/checkout_cart.html', context)
    
@login_required
@transaction.atomic
def save_order_from_cart(request):
    if request.method == 'POST': # 주문하기 버튼이 눌린 경우
        # 구매자 정보 불러오기
        user = request.user
        # 카트 불러오기
        cart = Cart.objects.get(customer=user)
        # 카트 아이템 불러오기
        cart_items = CartItem.objects.filter(cart=cart)
        
        # 데이터베이스에서 가져온 제품 정보를 모아둘 리스트 생성
        product_list = []
        # 제품 재고 확인
        for item in cart_items:
            product = Product.objects.get(product_id=item.product.product_id) # 데이터베이스에서 새로 가져옴, 최신값 확인
            # 선택한 모든 상품의 재고가 충분할 때
            if product.stock >= int(item.quantity): # 재고가 충분한지 확인
                product_list.append((product, int(item.quantity)))
                # 또는 pass 후 아래서 다시 product를 DB에서 가져옴 (배열 계산이 디비서버 통신보다 빠를것으로 예상)
            else: # 일부 상품이라도 재고가 부족할 때
                return JsonResponse({'success': False, 'message': '현재 상품의 재고가 충분하지 않습니다'})
        
        # 배송 정보 불러오기
        shipping_address = request.POST.get('shipping_address')
        shipping_address_detail = request.POST.get('shipping_address_detail')
        postal_code = request.POST.get('postal_code')
        recipient = request.POST.get('recipient')
        recipient_phone_number = request.POST.get('recipient_phone_number')
        # 결제 정보 불러오기
        payment_method = request.POST.get('payment_method')
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
        # 모든 주문 아이템 생성
        for product, quantity in product_list:
            OrderItem.objects.create(
                    order = order,
                    product=product,
                    quantity=quantity
                )  
        # 입력한 주소 배송지 목록에 저장하기
        shipping_address = ShippingAddress.objects.create(
                    customer = user,
                    shipping_address = shipping_address + ' ' + shipping_address_detail,
                    postal_code = postal_code,
                    recipient = recipient,
                    recipient_phone_number = recipient_phone_number
                )
            
        return JsonResponse({'success': True, 'message': '결제가 완료되어야 구매가 완료됩니다.', 'order_id': order.order_id}) # 메세지는 사용 안됨

@login_required
@transaction.atomic
def save_payment_from_cart(request):
    if request.method == 'POST': # 주문하기 버튼이 눌린 경우
        # 구매자 정보 불러오기
        user = request.user
        # 카트 불러오기
        cart = Cart.objects.get(customer=user)
        # 카트 아이템 불러오기
        cart_items = CartItem.objects.filter(cart=cart)
        # 결제가 된 주문 가져오기
        order_id = request.POST.get('order_id')
        order = Order.objects.get(order_id=order_id)

        # 변경사항을 모아둘 리스트 생성
        stock_updates = []
        # 제품 재고 변경 # 동시성처리
        for item in cart_items:
            # 상품들 락 설정
            product_udt = Product.objects.select_for_update(nowait=False).get(product_id=item.product.product_id) # 데이터베이스에서 새로 가져옴, 최신값 확인
            # 주문하는 모든 상품의 재고가 충분할 때
            if product_udt.stock >= int(item.quantity): # 재고가 충분한지 확인
                stock_updates.append((product_udt, int(item.quantity)))
            else: # 일부 상품의 재고가 부족할 때
                order.order_status = '환불대기'
                order.save()
                return JsonResponse({'success': False, 'message': '현재 상품의 재고가 충분하지 않습니다. 영업일 2일 이내로 환불을 도와드리겠습니다.'}) 

        # 모든 제품의 재고가 충분할 때 재고 업데이트/변경
        for product_udt, quantity in stock_updates:
            product_udt.stock -= quantity
            product_udt.save()

        order.order_status = '결제완료'
        order.save()

        imp_uid = request.POST.get('imp_uid')
        merchant_uid = request.POST.get('merchant_uid')
        # paid_amount = request.POST.get('paid_amount') # 실제로 결제된 금액(현재 100원)
        total_final_price_str = request.POST.get('total_final_price') # 결제 금액
        paid_amount = int(float(total_final_price_str))  # 숫자로 변환

        # 결제 내역 저장
        Payment.objects.create(
                    order = order,
                    paid_amount = paid_amount, 
                    imp_uid = imp_uid, 
                    merchant_uid = merchant_uid
                )
        
        # 카트 아이템 삭제
        for item in cart_items:
            item.delete()
            
        return JsonResponse({'success': True, 'message': 'Payment created successfully', 'order_id': order.order_id}) # 메시지는 안쓰임

def order_success(request):
    # 결제가 된 주문 가져오기

    # 수정할 사항 : user 정보 넣어야함. 내것만 확인가능하도록

    order_id = request.GET.get('order_id')
    order = Order.objects.get(order_id=order_id)   
    order_items = OrderItem.objects.filter(order = order)
    payment = Payment.objects.get(order=order)
        
    context={
        'order' : order,
        'order_items' : order_items,
        'payment' : payment
        }

    return render(request, 'customer/order_confirmation.html', context)

def order_fail(request):
    if request.method == 'POST':
        # 수정할 order가져오기
        order_id = request.POST.get('order_id')
        order_status = request.POST.get('order_status')
        err_message = request.POST.get('err_message')
        # order_status 수정하기
        order = Order.objects.get(order_id=order_id)
        order.order_status = order_status
        order.save()
        # 사용자에게 안내할 메세지
        context={
            'message' : err_message,
            }
        return render(request, 'customer/order_fail.html', context)

# 로그인한 고객의 전체 주문 내역
@login_required
def my_shopping_list(request):
    if request.method == 'GET':
        # 구매자 정보 불러오기
        user = request.user
        # 구매자의 모든 주문 가져오기
        orders = Order.objects.filter(customer=request.user) \
        .prefetch_related('orderitem_set__product', 'payment_set')
        context={
            'orders' : orders,
            }
        return render(request,"customer/my_shopping.html", context)
    
# 결제 관련 rest api 인증 정보 
load_dotenv() 
rest_api_imp=os.getenv("PAYMENT_REST_API_IMP")
rest_api_key=os.getenv("PAYMENT_REST_API_KEY")
rest_api_secret=os.getenv("PAYMENT_REST_API_SECRET")

# 액세스 토큰 발급 함수
def get_access_token():
    url = "https://api.iamport.kr/users/getToken"
    payload = {
        'imp_key': rest_api_key,
        'imp_secret': rest_api_secret
    }
    response = requests.post(url, data=payload)
    return response.json().get('response').get('access_token')

# 주문 취소 (결제된 상품이면 환불 포함)
@login_required
@transaction.atomic
def cancel_order(request, order_id):
    # 결제완료(카드)일 경우만 주문 취소 기능 활성화 + 결제대기(통장)의 경우 추가 가능
    order = get_object_or_404(Order, pk=order_id, customer=request.user)
    if order.order_status not in ['결제완료', '부분환불']:
        return JsonResponse({'code': 1, 'message': '주문 취소가 불가능한 상태입니다.'})
    
    # 취소/환불할 상품의 결제 정보가져오기 (결제가 완료된 상태에 한해 진행 중)
    payment = Payment.objects.get(order=order)
    imp_uid = payment.imp_uid
    item_types_count = order.orderitem_set.count() # 테스트용 결제 금액 계산용

    # api 통신 토큰 생성 (30분 유효)
    token = get_access_token()
    url = f"https://api.iamport.kr/payments/cancel"
    headers = {
        "Content-Type": "application/json",
        'Authorization': token
    }
    payload = {
        'imp_uid': imp_uid,  # 포트원 주문번호
        'amount' : 100*item_types_count, # 취소한 상품의 결제 금액만큼 취소 (부분취소는 orderitem 구조에 결제상태&환불금액 정보 기입후 사용)
        'reason': '고객 요청', 
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # HTTPError 발생 시 예외 처리
    except requests.exceptions.RequestException as e:
        return JsonResponse({'code': 2, 'message': f'API 요청 중 오류가 발생했습니다: {str(e)}'})
    
    result = response.json()
    if result.get('code') != 0:
        # API에서 오류가 발생한 경우
        return JsonResponse({'code': 3, 'message': f'결제 취소 중 오류가 발생했습니다: {result.get("message")}'})

    # 모델 수정 후 부분 취소 가능
    # # 결제 금액과 취소 금액 비교하여 주문 상태 업데이트
    # cancel_amount = result.get('response', {}).get('cancel_amount', 0)
    # if cancel_amount >= payment.paid_amount:
    #     order.order_status = '환불완료'
    # else:
    #     order.order_status = '부분환불'
    # order.save()

    # 전체 환불처리
    order.order_status = '환불완료'
    order.save()

    return JsonResponse(response.json())

