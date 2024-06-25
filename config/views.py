from django.views.generic import ListView
from seller.models import *
from customer.models import *
###############   
from django.views.generic.base import TemplateView
# auth 모듈에 없는 가입 처리용 뷰 UserCreateView와 UserCreateDoneTV 코딩
from django.views.generic import CreateView # 테이블에 새로운 레코드 생성하기 위해 필요한 폼 보여주고, 입력된 데이터를 레코드로 생성하는 뷰, 테이블 변경 처리 관련
from django.contrib.auth.forms import UserCreationForm # User 모델의 객체를 생성하기 위해 보여주는 폼
from django.urls import reverse_lazy # reverse_lazy : 함수 인자로 url패턴명을 받음
from customer.forms import SignupForm
from django.db.models import Count
import random
from django.core.cache import cache
from config.recommend_algorithm import *


class HomeView(ListView):

    template_name = 'home.html'

    def get_queryset(self):
        product_queryset = Product.objects.all()
        category_queryset = Category.objects.all()
        customer_queryset = Customer.objects.all()
        return list(product_queryset) + list(category_queryset) + list(customer_queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        if self.request.user.is_authenticated:
            likes = Like.objects.all()
            reviews = Review.objects.all()
            likes_customer_ids = likes.values_list('customer', flat=True).distinct()
            reviews_customer_ids = reviews.values_list('customer', flat=True).distinct()

            if  self.request.user.id in likes_customer_ids or self.request.user.id in reviews_customer_ids:       
                context['cf_products'] = cf_products(user_id=self.request.user.id, num_product=6) 
                context['mf_products'] = mf_products(user_id=self.request.user.id) 
            else:
                context['popular_products'] = get_popular_products()
                context['random_products'] = self.get_random_products()     
            
            cache_key = f'recently_viewed_{self.request.user.id}'
            recently_viewed_ids = cache.get(cache_key, [])
            context['recently_viewed_products'] = Product.objects.filter(product_id__in=recently_viewed_ids)
        else:
            context['popular_products'] = get_popular_products()
            context['random_products'] = self.get_random_products()

        context['current_category'] = ''
        return context

    def get_random_products(self):
        all_products = list(Product.objects.all())
        return random.sample(all_products, min(len(all_products), 6))







class UserCreateView(CreateView): # CreateView 상속받아 클래스형 뷰 생성 
    template_name = 'registration/register.html' # 템플릿 이름 지정
    # form_class = UserCreationForm # 장고의 기본 폼 사용
    form_class = SignupForm # 장고의 기본 폼 사용하면 에러 발생 노션 4.27 페이지 참조
    success_url = reverse_lazy('register_done') # 레코드 생성 완료된 후 이동할 URL 지정

class UserCreateDoneTV(TemplateView):
    template_name = 'registration/register_done.html'


    
