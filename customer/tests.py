from django.test import TestCase, RequestFactory
from django.urls import reverse
from .models import *
from seller.models import *
from customer.views import add_to_cart
from .forms import CartItemForm

class AddToCartTests(TestCase):
    def setUp(self): # 사용자와 제품 생성

        # Membership 객체 생성 (foreign key 참조를 위해 필요)
        self.membership = Membership.objects.create(
            membership_id=1,
            grade='test',
            member_discount_rate=1
        )

        self.customer = Customer.objects.create_user(
            membership_id=self.membership.membership_id,
            customer_name='testcustomer',
            username='testcustomer',
            email='testcustomer@naver.com',
            phone_number='01011112222'

        )

        # Seller 유저 생성
        self.seller = Seller.objects.create_user(
            company_name='testcompany',
            registration_number='123412341234',
            username='testseller',
            email='testseller@naver.com',
            phone_number='01022223333'

        )

        # Category 객체 생성
        self.category = Category.objects.create(
            category_id=1,
            category_name='testcategory'
        )
        # Product 객체 생성
        self.product = Product.objects.create(
            product_id=1,
            seller=self.seller,
            seller_id_copy=self.seller.id,
            category=self.category,
            product_name='Test Product',
            price=10000,
            description='This is a test product.',
            is_visible=True,
            stock=50,
            discount_rate=0.10,
            is_option=True
        )

        # 장바구니 추가 URL
        self.add_to_cart_url = reverse('customer:add_to_cart')

        # RequestFactory 인스턴스 생성
        self.factory = RequestFactory()

        # cart와 cartitem 생성


    def test_add_item_to_cart_authenticated(self): # 인증된 사용자가 제품을 장바구니에 성공적으로 추가할 수 있는지 테스트
        # self.client.login(username=self.customer.username, password=self.customer.password)
        # response = self.client.post(self.add_to_cart_url, {'product_id': self.product.product_id, 'quantity': 1})
        
        # POST 요청 데이터 준비
        data = {
            'product_id': self.product.product_id,
            'quantity': 1
        }
        
        # RequestFactory를 사용하여 POST 요청 생성
        request = self.factory.post(self.add_to_cart_url, data=data)

        # request.user에 self.customer 할당
        request.user = self.customer

        # add_to_cart 뷰 함수 직접 호출
        response = add_to_cart(request)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Item added to cart successfully', 'added': True})

        cart = Cart.objects.get(customer_id=self.customer.id)
        cart_item = CartItem.objects.get(cart_id=cart.cart_id, product_id=self.product.product_id)

        self.assertEqual(cart_item.quantity, 1)

    def test_add_item_to_cart_invalid_quantity(self): # 유효하지 않은 수량을 요청했을 때, 에러가 발생하는지 테스트
        
        # POST 요청 데이터 준비
        data = {
            'product_id': self.product.product_id,
            'quantity': -1 # -1 이라는 유요하지 않은 수량
        }
        
        # RequestFactory를 사용하여 POST 요청 생성
        request = self.factory.post(self.add_to_cart_url, data=data)

        # request.user에 self.customer 할당
        request.user = self.customer

        # add_to_cart 뷰 함수 직접 호출
        response = add_to_cart(request)
        self.assertEqual(response.status_code, 400)

        form = CartItemForm(request.POST)
        form.is_valid()  # 폼을 유효성 검사하기 위해 호출
        self.assertJSONEqual(response.content, {'message': form.errors['quantity'][0]})

    def test_add_item_to_cart_unauthenticated(self):# 인증되지 않은 사용자가 요청을 보냈을 때 에러가 발생하는지  
        response = self.client.post(self.add_to_cart_url, {'product_id': self.product.product_id, 'quantity': 1})
        self.assertEqual(response.status_code, 401)  # 로그인 페이지로 리다이렉트되는지 확인