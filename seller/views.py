from django.shortcuts import render,redirect
from .models import Product, Seller, Category,ProductImage
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from customer.models import  Order, OrderItem
from config import settings
import os
from .forms import SellerSignupForm
from django.http import HttpResponse
from seller.backends import SellerAuthenticationBackend
from django.contrib.auth import login,logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
# from django.contrib import messages
from customer.models import MyUser
from django.db.models import Q, Prefetch
from django.contrib.auth.decorators import login_required

def seller_index(request):    
    product = Product.objects.filter(seller=request.user)
    category = Category.objects.all()
    product_iamge = ProductImage.objects.all()
    context={
        'products': product,
        'categories' : category,
        'product_images' : product_iamge,
    }
    return render(request, 'seller/seller_index.html', context)

def add_product(request):
   # get
    if request.method=='GET':
        category = Category.objects.all()
        seller = Seller.objects.all()
        product = Product.objects.all()
        context={            
            'categories' : category,
            'sellers' : seller,
            'products' : product
        }
        return render(request, 'seller/seller_add_product.html', context)
    # post
    elif request.method=="POST":
        # 내용 추가
        seller = Seller.objects.get(id=request.user.id)        
        category_id = request.POST.get('category')  
        category = Category.objects.get(category_id=category_id)        
        product_name = request.POST['product_name']
        price = request.POST['price']
        description = request.POST['description']        
        is_visible = True
        if request.POST['is_visible'] == '노출':
            is_visible = True
        elif request.POST['is_visible'] == '비노출':
            is_visible = False
        stock = request.POST['stock']
        discount_rate = request.POST['discount_rate']
        is_option = True
        if request.POST['is_option'] == '있음':
            is_option = True
        elif request.POST['is_option'] == '없음':
            is_option = False        

        product = Product.objects.create(seller=seller,category=category,product_name=product_name, price =price , description=description,is_visible=is_visible,stock=stock,discount_rate=discount_rate,is_option=is_option)    

        # 이미지 저장 및 url 설정 내용
        fs=FileSystemStorage()
        uploaded_files = request.FILES.getlist('files')
        image_urls = []

        for uploaded_file in uploaded_files:            
            filename = fs.save(uploaded_file.name, uploaded_file)
            image_url = fs.url(filename)
            image_urls.append(image_url)

        for image_url in image_urls:
            fs.save(uploaded_file.name, uploaded_file)
            ProductImage.objects.create(product=product, image_url=image_url)                      
        
        return redirect('seller:seller_index')  
    

def order_manage(request):

    seller = Seller.objects.get(id=request.user.id)            
    sold_products = (
        Order.objects.filter(orderitem__product__seller=seller)
        .distinct()
        .prefetch_related(
            Prefetch('orderitem_set', queryset=OrderItem.objects.select_related('product'))
        )
    )
    context = {'sold_products': sold_products}    
    return render(request, 'seller/seller_order_manage.html', context)

@login_required
def edit_product(request, product_id):
    try:
        product = Product.objects.get(product_id=product_id)
        existing_images = ProductImage.objects.filter(product=product)

        if product.seller != request.user:
            messages.error(request, "자신이 등록한 상품만 수정할 수 있습니다.")
            return redirect('seller:seller_index')
    except Product.DoesNotExist:
        messages.error(request, "수정하려는 상품이 존재하지 않습니다.")
        return redirect('seller:seller_index')

    if request.method == 'POST':
        # 정보 가져오기
        product_name = request.POST['product_name']
        price = request.POST['price']
        description = request.POST['description']
        is_visible = request.POST.get('is_visible', False)  
        stock = request.POST['stock']
        discount_rate = request.POST['discount_rate']
        is_option = request.POST.get('is_option', False)  

        # 정보 업데이트
        product.product_name = product_name
        product.price = price
        product.description = description
        product.is_visible = is_visible
        product.stock = stock
        product.discount_rate = discount_rate
        product.is_option = is_option
        product.save()
                
        uploaded_files = request.FILES.getlist('files')

        # 삭제할 이미지 목록
        delete_image_ids = request.POST.getlist('delete_image_ids')

        if delete_image_ids and any(delete_image_ids):
            # 기존 이미지 삭제
            for delete_image_id in delete_image_ids:
                try:
                    if delete_image_id == '':
                        break
                    delete_image = ProductImage.objects.get(productimage_id=delete_image_id)
                    fs = FileSystemStorage()
                    base_dir = settings.MEDIA_ROOT                    
                    #delete_url = os.path.join(base_dir, delete_image.image_url)
                    delete_url = os.path.join(base_dir, delete_image.image_url.lstrip('/media/'))    
                    fs.delete(delete_url)  # 이미지 파일 삭제
                    delete_image.delete()
                except ProductImage.DoesNotExist:
                    pass  # 삭제하려는 이미지가 없는 경우 에러 처리 무시

        # 새로운 이미지 저장
        
        if uploaded_files:
            fs=FileSystemStorage()
            image_urls = []
            for uploaded_file in uploaded_files:
                filename = fs.save(uploaded_file.name, uploaded_file)
                image_url = fs.url(filename)
                image_urls.append(image_url)

            for image_url in image_urls:
                ProductImage.objects.create(product=product, image_url=image_url)

            messages.success(request, "상품 정보가 수정되었습니다.")
            return redirect('seller:seller_index') 

    context = {
        'product': product,
        'existing_images': existing_images,  # 템플릿에 기존 이미지 정보 전달
    }
    return render(request, 'seller/seller_edit_product.html', context)

def delete_product(request, product_id):
    object=Product.objects.get(product_id=product_id)
    object.delete()
    return redirect('seller:seller_index')


def seller_signup_view(request):
    if request.method == 'POST':
        form = SellerSignupForm(request.POST)
        if form.is_valid():
            form.save()
            # 회원가입 성공 메시지 추가 예정            
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
        seller = backend.authenticate(request,username=username, password=password)
        
        if seller is not None:  # 인증 성공
            login(request, seller, backend='seller.backends.SellerAuthenticationBackend')
            return redirect('seller:seller_mypage')
        else:
            return HttpResponse('로그인 실패. 판매자 계정 정보를 확인해주세요.')
    
    else:
        # GET 요청일 경우 로그인 폼을 보여주는 페이지를 렌더링
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
            update_session_auth_hash(request, user)  # 비밀번호가 변경된 후에도 사용자가 로그아웃되지 않도록            
            # messages.success(request, "판매자 비밀번호 변경 성공")
            return redirect('seller:seller_mypage')
        else:
            # messages.error(request, "판매자 비밀번호 변경에 실패하였습니다. 다시 시도 해주세요.")
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
            # 만약 제출된 이메일이 현재 사용자를 제외한 다른 사용자에 의해 이미 사용되고 있다면 
            # 오류 메시지를 설정하고 리디렉션
            # messages.error(request, "입력하신 이메일은 이미 사용 중입니다.")
            return redirect('seller:seller_profile_edit')        
        user.email = new_email

        new_phone_number = request.POST.get("phone_number")      
        if MyUser.objects.filter(~Q(pk=user.pk), phone_number=new_phone_number).exists():            
            # messages.error(request, "입력하신 휴대폰 번호는 이미 사용 중입니다.")
            return redirect('seller:seller_profile_edit')        
        user.phone_number = new_phone_number
        
        user.save()        
        
        seller = Seller.objects.get(pk=user.pk)
        # 판매자 정보 수정
        seller.company_name = request.POST.get("company_name")
        seller.business_contact = request.POST.get("business_contact")          
        seller.registration_number  = request.POST.get("registration_number")
        # 수정사항 저장
        seller.save()
        
        # messages.success(request, "프로필이 성공적으로 업데이트되었습니다.")
        return redirect('seller:seller_mypage')
    else:
        if not request.user.is_authenticated:
            # 로그인하지 않은 사용자는 로그인 페이지로 리다이렉트
            return redirect('seller:seller_login')

        try:
            # 현재 로그인한 사용자로부터 Seller 정보를 가져옵니다.
            seller = Seller.objects.get(pk=request.user.pk)
        except Seller.DoesNotExist:
            # Seller 정보가 존재하지 않을 경우 처리
            seller = None       

        context = {                       
            'company_name': seller.company_name if seller else "비어있음",
            'business_contact':seller.business_contact if seller else "비어있음",
            'registration_number':seller.registration_number if seller else "비어있음",        
        }
        
        return render(request, 'seller/seller_profile_edit.html', context)

def delete_seller_view(request):
    if request.method == 'POST' and request.POST['delete_seller?'] == '판매자탈퇴':
        # 현재 로그인한 사용자를 삭제합니다.
        user = request.user
        user.delete()
        # messages.success(request, '계정이 성공적으로 삭제되었습니다.')
        return redirect('seller:seller_login')
    else:
        # messages.error(request, '계정이 삭제가 실패했습니다.')
        return render(request, 'seller/delete_seller.html')