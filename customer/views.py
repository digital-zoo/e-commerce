from django.shortcuts import render
from django.views.generic import ListView
from seller.models import *
from customer.models import*
from django.db.models import Sum, F

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
    
def cart(request, pk):
    # user = request.user
    # cart, created = Cart.objects.get_or_create(customer_id=user.id)

    # cartitem = CartItem.objects.filter(cart_id=cart.cart_id)

    # if len(cartitem):
    #     print('nothing')
    # else:
    #     print('물건있음')

    # pass
    cart, created = Cart.objects.get_or_create(customer_id=pk) # get
    cartitem = CartItem.objects.filter(cart_id=cart.cart_id)
    total_price = CartItem.objects.all().annotate(item_total=F('quantity') * F('product__price')).aggregate(total=Sum('item_total'))['total']
    context = {
        'object' : cartitem,
        'total_price' : total_price
    }
    return render(request, 'customer/cart_list.html', context)

def product_detail(request, pk):
    product = Product.objects.get(product_id=pk)
    context = {
        'object' : product
    }

    return render(request, 'customer/product_detail.html', context)

from django.http import JsonResponse

def add_to_cart(request):
    user = request.user
    product_id = request.POST['product_id']
    product = Product.objects.get(product_id=product_id)
    
    cart, cart_created = Cart.objects.get_or_create(customer_id=user.id)
    cartitem, caritem_created = CartItem.objects.get_or_create(cart_id=cart.cart_id, product_id=product_id, defaults={'quantity':0})
    cartitem.quantity += int(request.POST['quantity'])
    cartitem.save()
    
    return JsonResponse({'message': 'Item added to cart successfully', 'added': True}, status=200)