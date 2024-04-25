from django.views.generic import ListView
from seller.models import *

class HomeView(ListView):
    template_name='home.html'
    paginate_by=2

    #필요한 데이터 가져오기
    def get_queryset(self):
        product_queryset = Product.objects.all()
        category_queryset = Category.objects.all()
        return list(product_queryset) + list(category_queryset)
    
    #데이터를 html로 넘기기
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['categories'] = Category.objects.all()
        #첫화면에는 선택된 카테고리 없음
        context['current_category'] = ''
        return context
    
