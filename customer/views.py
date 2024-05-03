from django.shortcuts import render
from django.views.generic import ListView
from seller.models import *
from .models import *
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect

# # 테스트용 가상 로그인
# def simulate_login(request):
#     # 기존에 생성한 사용자 정보 
#     username = 'kkk'
#     password = '1'

#     # 해당 사용자로 로그인 시도
#     user = authenticate(username=username, password=password)
#     if user is not None:
#         # 로그인 성공 시 세션에 사용자 정보 저장
#         login(request, user)
#         # return render(request, 'customer/checkout.html', {'user' : user})
#     else:
#         # 로그인 실패 시 오류 메시지 추가
#         print('로그인 실패했습니다')

# def s_logout(request):
#     next_page = request.GET.get('next')
#     if request.user.is_authenticated:
#         # 로그인되어 있는 경우 로그아웃 수행
#         print("로그아웃 성공적으로 진행함")
#         logout(request)
#     if next_page:
#         # 로그아웃 후에 이전 페이지로 리다이렉션됩니다.
#         return redirect(next_page)
#     else:
#         # 이전 페이지가 없으면 홈페이지로 리다이렉션됩니다.
#         return redirect('home')  # 이 부분에서 적절한 리다이렉션 대상을 설정해야 합니다.

        
  

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

from django.shortcuts import redirect
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse

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

def quick_checkout(request):
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


