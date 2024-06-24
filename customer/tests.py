from django.test import TestCase, RequestFactory
from django.urls import reverse
from .models import *
from seller.models import *
from customer.views import add_to_cart
from .forms import CartItemForm

# class AddToCartTests(TestCase):
#     def setUp(self): # 사용자와 제품 생성

#         # Membership 객체 생성 (foreign key 참조를 위해 필요)
#         self.membership = Membership.objects.create(
#             membership_id=1,
#             grade='test',
#             member_discount_rate=1
#         )

#         self.customer = Customer.objects.create_user(
#             membership_id=self.membership.membership_id,
#             customer_name='testcustomer',
#             username='testcustomer',
#             email='testcustomer@naver.com',
#             phone_number='01011112222'

#         )

#         # Seller 유저 생성
#         self.seller = Seller.objects.create_user(
#             company_name='testcompany',
#             registration_number='123412341234',
#             username='testseller',
#             email='testseller@naver.com',
#             phone_number='01022223333'

#         )

#         # Category 객체 생성
#         self.category = Category.objects.create(
#             category_id=1,
#             category_name='testcategory'
#         )
#         # Product 객체 생성
#         self.product = Product.objects.create(
#             product_id=1,
#             seller=self.seller,
#             seller_id_copy=self.seller.id,
#             category=self.category,
#             product_name='Test Product',
#             price=10000,
#             description='This is a test product.',
#             is_visible=True,
#             stock=50,
#             discount_rate=0.10,
#             is_option=True
#         )

#         # 장바구니 추가 URL
#         self.add_to_cart_url = reverse('customer:add_to_cart')

#         # RequestFactory 인스턴스 생성
#         self.factory = RequestFactory()

#         # cart와 cartitem 생성


#     def test_add_item_to_cart_authenticated(self): # 인증된 사용자가 제품을 장바구니에 성공적으로 추가할 수 있는지 테스트
#         # self.client.login(username=self.customer.username, password=self.customer.password)
#         # response = self.client.post(self.add_to_cart_url, {'product_id': self.product.product_id, 'quantity': 1})
        
#         # POST 요청 데이터 준비
#         data = {
#             'product_id': self.product.product_id,
#             'quantity': 1
#         }
        
#         # RequestFactory를 사용하여 POST 요청 생성
#         request = self.factory.post(self.add_to_cart_url, data=data)

#         # request.user에 self.customer 할당
#         request.user = self.customer

#         # add_to_cart 뷰 함수 직접 호출
#         response = add_to_cart(request)

#         self.assertEqual(response.status_code, 200)
#         self.assertJSONEqual(response.content, {'message': 'Item added to cart successfully', 'added': True})

#         cart = Cart.objects.get(customer_id=self.customer.id)
#         cart_item = CartItem.objects.get(cart_id=cart.cart_id, product_id=self.product.product_id)

#         self.assertEqual(cart_item.quantity, 1)

#     def test_add_item_to_cart_invalid_quantity(self): # 유효하지 않은 수량을 요청했을 때, 에러가 발생하는지 테스트
        
#         # POST 요청 데이터 준비
#         data = {
#             'product_id': self.product.product_id,
#             'quantity': -1 # -1 이라는 유요하지 않은 수량
#         }
        
#         # RequestFactory를 사용하여 POST 요청 생성
#         request = self.factory.post(self.add_to_cart_url, data=data)

#         # request.user에 self.customer 할당
#         request.user = self.customer

#         # add_to_cart 뷰 함수 직접 호출
#         response = add_to_cart(request)
#         self.assertEqual(response.status_code, 400)

#         form = CartItemForm(request.POST)
#         form.is_valid()  # 폼을 유효성 검사하기 위해 호출
#         self.assertJSONEqual(response.content, {'message': form.errors['quantity'][0]})

#     def test_add_item_to_cart_unauthenticated(self):# 인증되지 않은 사용자가 요청을 보냈을 때 에러가 발생하는지  
#         response = self.client.post(self.add_to_cart_url, {'product_id': self.product.product_id, 'quantity': 1})
#         self.assertEqual(response.status_code, 401)  # 로그인 페이지로 리다이렉트되는지 확인


from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from requests_mock import Mocker
from requests.exceptions import RequestException
from django.contrib.auth.models import User
from customer.models import Order, OrderItem, Payment
from customer.views import get_access_token
from datetime import date
from decimal import Decimal
import os
import requests
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()
# 환경 변수 읽기
rest_api_key = os.getenv("PAYMENT_REST_API_KEY")
rest_api_secret = os.getenv("PAYMENT_REST_API_SECRET")

class CancelOrderTestCase(TestCase):

    # 테스트에 필요한 사용자, 주문 등의 데이터 설정
    def setUp(self):
        self.membership = Membership.objects.create(
            membership_id=1,
            grade='test',
            member_discount_rate=0.1
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

        # 주문 생성
        self.order = Order.objects.create(
            customer=self.customer,
            order_date=date.today(),
            order_status='결제완료',
            shipping_address='서울특별시 강남구',
            postal_code='12345',
            recipient='홍길동',
            recipient_phone_number='010-1234-5678',
            payment_method='card'
        )

        # 주문 항목 생성
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name=self.product.product_name,
            product_price=self.product.price * (1 - self.product.discount_rate),
            quantity=1,
            is_refunded=False
        )

        # 결제 생성
        self.payment = Payment.objects.create(
            order=self.order,
            paid_amount=100,
            imp_uid='test_imp_uid',
            merchant_uid='test_merchant_uid'
        )

        

    def get_access_token(self):
        # 실제 REST API를 호출하여 토큰 받기
        url = "https://api.iamport.kr/users/getToken"
        payload = {
            'imp_key': rest_api_key,
            'imp_secret': rest_api_secret
        }
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
            return response.json().get('response').get('access_token')
        except RequestException as e:
            print(f"Error while fetching access token: {e}")
            return None

    def test_cancel_order_success(self):
        access_token = self.get_access_token()

        if access_token:
            url = f"https://api.iamport.kr/payments/cancel/{self.payment.imp_uid}"
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            data = {
                'reason': '테스트 환불 요청'
            }

            try:
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
                json_response = response.json()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(json_response['code'], 0)
                self.assertEqual(json_response['message'], '주문 아이템이 성공적으로 취소되었습니다.')

                # 주문 상태 확인
                updated_order = Order.objects.get(pk=self.order.pk)
                self.assertEqual(updated_order.order_status, '환불완료')

                # 주문 아이템 상태 확인
                updated_order_item = OrderItem.objects.get(pk=self.order_item.pk)
                self.assertTrue(updated_order_item.is_refunded)

            except RequestException as e:
                self.fail(f"Request failed: {e}")

    def test_cancel_order_api_failure(self):
        access_token = self.get_access_token()

        if access_token:
            url = f"https://api.iamport.kr/payments/cancel/{self.payment.imp_uid}"
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            data = {
                'reason': '테스트 환불 요청'
            }

            try:
                # 모의 API 응답 설정
                mock_response = {
                    'code': 1,
                    'message': 'API Error',
                }

                with Mocker() as m:
                    m.post(url, json=mock_response, status_code=400)

                    # 주문 취소 요청
                    response = requests.post(url, headers=headers, json=data)

                # HTTP 응답 코드 확인
                self.assertEqual(response.status_code, 200)

                # JSON 응답 데이터 확인
                json_response = response.json()
                self.assertEqual(json_response['code'], 3)
                self.assertEqual(json_response['message'], '결제 취소 중 오류가 발생했습니다: API Error')

                # 주문 상태 및 주문 아이템 상태 확인 (변경되지 않아야 함)
                updated_order = Order.objects.get(pk=self.order.pk)
                self.assertNotEqual(updated_order.order_status, '환불완료')

                updated_order_item = OrderItem.objects.get(pk=self.order_item.pk)
                self.assertFalse(updated_order_item.is_refunded)

            except RequestException as e:
                self.fail(f"Request failed: {e}")