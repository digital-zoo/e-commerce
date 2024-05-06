from django.shortcuts import render, redirect
from django.views.generic import ListView
from seller.models import *
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from .forms import SignupForm
from django.views import View
from .models import Customer,Membership

from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
            messages.error(request, '로그인 실패. 다시 시도해주세요.')
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
            messages.error(request, "입력하신 이메일은 이미 사용 중입니다.")
            return redirect('customer:profile_edit')        
        user.email = new_email

        new_phone_number = request.POST.get("phone_number")      
        if MyUser.objects.filter(~Q(pk=user.pk), phone_number=new_phone_number).exists():            
            messages.error(request, "입력하신 휴대폰 번호는 이미 사용 중입니다.")
            return redirect('customer:profile_edit')        
        user.phone_number = new_phone_number
        
        user.save()        
        
        customer = Customer.objects.get(pk=user.pk)
        customer.customer_name = request.POST.get("customer_name")
        customer.address = request.POST.get("address")
        customer.postal_code = request.POST.get("postal_code")
        customer.save()
        
        messages.success(request, "프로필이 성공적으로 업데이트되었습니다.")
        return redirect('customer:profile_edit')
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
            messages.success(request, "비밀번호 변경 성공")
            return redirect('customer:mypage')
        else:
            messages.error(request, "비밀번호 변경이 실패하였습니다.다시 시도 해주세요.")
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
        messages.success(request, '계정이 성공적으로 삭제되었습니다.')
        return redirect('home')
    else:
        messages.error(request, '계정이 삭제가 실패했습니다.')
        return render(request, 'customer/delete_customer.html')
    