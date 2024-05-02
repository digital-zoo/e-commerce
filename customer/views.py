from django.shortcuts import render
from django.views.generic import ListView
from seller.models import *
from .models import *
from django.db.models import Sum

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

def quick_checkout(request):
    # 선택한 상품 불러오기
    product_id = request.GET.get('product_id')
    product = Product.objects.get(product_id=product_id)
    # 선택한 상품 수량 불러오기
    quantity = request.GET.get('quantity')
    # 가격 계산하기
    discounted_price = product.price * (1-product.discount_rate)
    final_price = discounted_price * int(quantity)
    context = {
    'product': product,
    'quantity': quantity,
    'discounted_price' : discounted_price,
    'final_price' : final_price
    }
    return render(request, 'customer/checkout.html', context)
  
