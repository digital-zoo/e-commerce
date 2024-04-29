from django.shortcuts import render, redirect
from django.views.generic import ListView
from seller.models import *
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponse
from .forms import SignupForm
# from django.urls import reverse_lazy
from django.views import View

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
            return HttpResponse('로그인 실패. 다시 시도해주세요.')
    else:
        # GET 요청일 경우 로그인 폼을 보여주는 페이지를 렌더링
        return render(request,"customer/login.html")

def logout_view(request):
    logout(request)
    return redirect("customer:login")

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