from django.shortcuts import render, redirect
from .forms import SellerSignupForm
from django.http import HttpResponse
from seller.backends import SellerAuthenticationBackend

def seller_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # SellerAuthenticationBackend의 인스턴스를 생성하고 authenticate를 호출
        backend = SellerAuthenticationBackend()
        seller = backend.authenticate(request, username=username, password=password)
        
        if seller:  # 인증 성공
            #seller 로그인
            return redirect('seller:seller_mypage')
        else:
            return HttpResponse('로그인 실패. 판매자 계정 정보를 확인해주세요.')

    return render(request, 'seller/seller_login.html')

def seller_logout_view(request):
    #seller 로그아웃   
    return redirect("seller:seller_login")

def seller_signup_view(request):
    if request.method == 'POST':
        form = SellerSignupForm(request.POST)
        if form.is_valid():
            form.save()            
            return redirect('seller:seller_login')
    else:
        form = SellerSignupForm()
    return render(request, 'seller/seller_signup.html', {'form': form})

#마이페이지 mypage_view
def seller_mypage_view(request):
    return render(request,"seller/seller_mypage.html")