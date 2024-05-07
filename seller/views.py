from django.shortcuts import render,redirect
from .models import Product, Seller, Category,ProductImage
from django.core.files.storage import FileSystemStorage
#from django.contrib.auth.models import User
from django.contrib import messages
from customer.models import  Order, OrderItem




# Create your views here.
def seller_index(request):
    #product = Product.objects.filter(user=request.user)
    product = Product.objects.all()
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
        # 폼에서 전달되는 각 값을 뽑아와서 DB에 저장

        # Food 내용을 구성 영역
        # category = Category.objects.get(name=request.POST['category'])
        seller_id = request.POST.get('seller')  #  seller ID   
        seller = Seller.objects.get(id=seller_id)        
        category_id = request.POST.get('category')  # seller ID    
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
    
def edit_product(request, product_id):
    try:
        product = Product.objects.get(product_id=product_id)
        existing_images = ProductImage.objects.filter(product=product)
    except Product.DoesNotExist:
        messages.error(request, "수정하려는 상품이 존재하지 않습니다.")
        return redirect('seller:product_list')

    if request.method == 'POST':
        # 정보 가져오기
        product_name = request.POST['product_name']
        price = request.POST['price']
        description = request.POST['description']
        is_visible = request.POST.get('is_visible', False)  # checkbox 수정필요
        stock = request.POST['stock']
        discount_rate = request.POST['discount_rate']
        is_option = request.POST.get('is_option', False)  # checkbox 수정필요

        # 정보 업데이트
        product.product_name = product_name
        product.price = price
        product.description = description
        product.is_visible = is_visible
        product.stock = stock
        product.discount_rate = discount_rate
        product.is_option = is_option
        product.save()

        # 이미지 처리
        uploaded_files = request.FILES.getlist('files')

        # 삭제할 이미지 목록 (POST 파라미터에서 가져옴)
        delete_image_ids = request.POST.getlist('delete_image_ids')

        # 기존 이미지 삭제
        for delete_image_id in delete_image_ids:
            try:
                delete_image = ProductImage.objects.get(productimage_id=delete_image_id)
                storage = FileSystemStorage()
                storage.delete(delete_image.image_url)  # 이미지 파일 삭제
                delete_image.delete()
            except ProductImage.DoesNotExist:
                pass       

        # 새로운 이미지 저장
        # fs=FileSystemStorage()
        # for uploaded_file in uploaded_files:
        #     filename = fs.save(uploaded_file.name, uploaded_file)
        #     image_url = fs.url(filename)
        #     ProductImage.objects.create(product=product, image_url=image_url)

            

        messages.success(request, "상품 정보가 수정되었습니다.")
        return redirect('seller:seller_index')

    context = {
        'product': product,
        'existing_images': existing_images,  # 템플릿에 기존 이미지 정보 전달
    }
    return render(request, 'seller/seller_edit_product.html', context)
        

    #     messages.success(request, "상품 정보가 수정되었습니다.")
    #     return redirect('seller:seller_index')

    # context = {
    #     'product': product,
    # }
    # return render(request, 'seller/seller_edit_product.html', context)


def order_manage(request):

    seller_id = request.GET.get('seller')  
    seller = Seller.objects.get(id=8)   # 로그인 기능 구현시 수정 필요
    #seller = Seller.objects.get(user=request.user)  
    sold_products = Order.objects.filter(orderitem__product__seller=seller).distinct()  
    context = {'sold_products': sold_products}
    # 주문상태 변경 필요
    return render(request, 'seller/seller_order_manage.html', context)

