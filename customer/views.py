from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView
from django.db.models import Q
from seller.models import *
from customer.models import *
from django.http import HttpResponse

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



from django.http import JsonResponse

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
