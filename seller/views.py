from django.shortcuts import render,redirect
from .models import Product
from django.core.files.storage import FileSystemStorage


# Create your views here.
def seller_index(request):
    #product = Product.objects.filter(user=request.user)
    product = Product.objects.all()
    context={
        'object_list': product
    }
    return render(request, 'seller/seller_index.html', context)

def add_product(request):
   # get
    if request.method=='GET':
        return render(request, 'seller/seller_add_product.html')
    # post
    elif request.method=="POST":
        # 폼에서 전달되는 각 값을 뽑아와서 DB에 저장

        # Food 내용을 구성 영역
        # category = Category.objects.get(name=request.POST['category'])
        user=request.user
        food_name = request.POST['name']
        food_price = request.POST['price']
        food_description = request.POST['description']

        # 이미지 저장 및 url 설정 내용
        fs=FileSystemStorage()
        uploaded_file = request.FILES['file']
        name = fs.save(uploaded_file.name, uploaded_file)
        url = fs.url(name)

        Product.objects.create(user= user,name=food_name, price =food_price , description=food_description,image_url=url)    

        # food_name, price, description
        return redirect('seller:seller_index')