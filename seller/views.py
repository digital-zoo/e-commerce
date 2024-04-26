from django.shortcuts import render,redirect
from .models import Product, Seller, Category
from django.core.files.storage import FileSystemStorage
#from django.contrib.auth.models import User



# Create your views here.
def seller_index(request):
    #product = Product.objects.filter(user=request.user)
    product = Product.objects.all()
    category = Category.objects.all()
    context={
        'object_list': product,
        'categories' : category,
    }
    return render(request, 'seller/seller_index.html', context)

def add_product(request):
   # get
    if request.method=='GET':
        category = Category.objects.all()
        seller = Seller.objects.all()
        context={            
            'categories' : category,
            'sellers' : seller,
        }
        return render(request, 'seller/seller_add_product.html', context)
    # post
    elif request.method=="POST":
        # 폼에서 전달되는 각 값을 뽑아와서 DB에 저장

        # Food 내용을 구성 영역
        # category = Category.objects.get(name=request.POST['category'])
        seller_id = request.POST.get('seller')  # Get selected seller ID (string)    
        seller = Seller.objects.get(id=seller_id)        
        category_id = request.POST.get('category')  # Get selected seller ID (string)    
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

        # 이미지 저장 및 url 설정 내용
        fs=FileSystemStorage()
        #uploaded_file = request.FILES['file']
        #name = fs.save(uploaded_file.name, uploaded_file)
        #url = fs.url(name)

        Product.objects.create(seller=seller,category=category,product_name=product_name, price =price , description=description,is_visible=is_visible,stock=stock,discount_rate=discount_rate,is_option=is_option)    

        # food_name, price, description
        return redirect('seller:seller_index')
    

def make_seller(request):
    new_seller = Seller(username="판매자_사용자이름",email="판매자@example.com", phone_number="+821012345678", company_name="나의 회사",)

