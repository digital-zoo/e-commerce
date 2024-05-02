from django.shortcuts import render, redirect
from .forms import SellerSignupForm
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from django.contrib import messages
from seller.backends import SellerAuthenticationBackend

def seller_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # SellerAuthenticationBackend의 인스턴스를 생성하고 authenticate를 호출합니다.
        backend = SellerAuthenticationBackend()
        seller = backend.authenticate(request, username=username, password=password)
        
        if seller:  # 인증 성공
            # 인증된 사용자를 session에 등록합니다.
            login(request, seller, backend='seller.backends.SellerAuthenticationBackend')
            # return redirect('home')
            return HttpResponse('로그인 성공')
        else:
            return HttpResponse('로그인 실패. 판매자 계정 정보를 확인해주세요.')

    return render(request, 'seller/seller_login.html')

def seller_logout_view(request):
    logout(request)    
    return redirect("seller:seller_login")

def seller_signup_view(request):
    if request.method == 'POST':
        form = SellerSignupForm(request.POST)
        if form.is_valid():
            form.save()
            # 회원가입 후 로직을 추가하세요. 예: 로그인 페이지로 리다이렉트
            return redirect('seller:seller_login')
    else:
        form = SellerSignupForm()
    return render(request, 'seller/seller_signup.html', {'form': form})