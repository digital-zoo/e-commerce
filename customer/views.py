from django.shortcuts import render
from django.views.generic import ListView
from seller.models import *
from customer.models import *
from django.db.models import Sum, F, FloatField
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
    user = request.user
    product_id = request.POST['product_id']
    product = Product.objects.get(product_id=product_id)
    
    cart, cart_created = Cart.objects.get_or_create(customer_id=user.id)
    cartitem, caritem_created = CartItem.objects.get_or_create(cart_id=cart.cart_id, product_id=product_id, defaults={'quantity':0})
    cartitem.quantity += int(request.POST['quantity'])
    cartitem.save()
    
    return JsonResponse({'message': 'Item added to cart successfully', 'added': True}, status=200)

# 연희님 코드
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
