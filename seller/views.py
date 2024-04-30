from django.shortcuts import render, redirect
from .forms import SellerSignupForm
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponse

def seller_login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # 로그인 성공 후 리다이렉트할 페이지.
            return redirect('home') #구매자 페이지로 수정?
        else:
            # 실패한 경우, 로그인 페이지에 에러 메시지를 표시할 수 있습니다.
            return HttpResponse('로그인 실패. 다시 시도해주세요.')
    else:
        # GET 요청일 경우 로그인 폼을 보여주는 페이지를 렌더링
        return render(request,"seller/seller_login.html")

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