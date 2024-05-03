from django.shortcuts import render, redirect
from .forms import SellerSignupForm
from django.http import HttpResponse
from seller.backends import SellerAuthenticationBackend
from django.contrib.auth import login,logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

def seller_signup_view(request):
    if request.method == 'POST':
        form = SellerSignupForm(request.POST)
        if form.is_valid():
            form.save()            
            return redirect('seller:seller_login')
    else:
        form = SellerSignupForm()
    return render(request, 'seller/seller_signup.html', {'form': form})

def seller_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # SellerAuthenticationBackend의 인스턴스를 생성하고 authenticate를 호출
        backend = SellerAuthenticationBackend()
        seller = backend.authenticate(request, username=username, password=password)
        
        if seller:  # 인증 성공
            login(request, seller, backend='seller.backends.SellerAuthenticationBackend')
            return render(request,'seller/seller_mypage.html')
        else:
            return HttpResponse('로그인 실패. 판매자 계정 정보를 확인해주세요.')

    return render(request, 'seller/seller_login.html')

def seller_mypage_view(request):
    return render(request,"seller/seller_mypage.html")

def seller_logout_view(request):
    logout(request)
    return redirect("seller:seller_login")

def seller_change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # 중요: 비밀번호가 변경된 후에도 사용자가 로그아웃되지 않도록 함
            messages.success(request, "판매자 비밀번호 변경 성공")
            return redirect('seller:seller_mypage')
        else:
            messages.error(request, "비밀번호 변경에 실패하였습니다. 다시 시도 해주세요.")
            return redirect('seller:seller_change_password')
    else:
        form = PasswordChangeForm(request.user)
        return render(request, 'seller/seller_change_password.html', {'form': form})

def seller_profile_edit_view(request):
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

# delete_seller_view