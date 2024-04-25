from django.views.generic import ListView
from seller.models import *

class HomeView(ListView):
    template_name='home.html'
    paginate_by=2

    def get_queryset(self):
        product_queryset = Product.objects.all()
        category_queryset = Category.objects.all()
        return list(product_queryset) + list(category_queryset)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['categories'] = Category.objects.all()
        return context
    
