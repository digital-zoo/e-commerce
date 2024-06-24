from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import *
from seller.models import *
from customer.views import cancel_order
from datetime import date

class CancelOrderAPITests(TestCase):
    def setUp(self):
        # 필요한 모델 객체들을 생성합니다.

        # Membership 객체 생성
        self.membership = Membership.objects.create(
            membership_id=1,
            grade='test',
            member_discount_rate=1  # 10% 할인율
        )

        # 고객 객체 생성
        self.customer = Customer.objects.create_user(
            membership_id=self.membership.membership_id,
            customer_name='testcustomer',
            username='testcustomer',
            email='testcustomer@naver.com',
            phone_number='01011112222'
        )

        # 판매자 객체 생성
        self.seller = Seller.objects.create_user(
            company_name='testcompany',
            registration_number='123412341234',
            username='testseller',
            email='testseller@naver.com',
            phone_number='01022223333'
        )

        # 카테고리 객체 생성
        self.category = Category.objects.create(
            category_id=1,
            category_name='testcategory'
        )

        # 상품 객체 생성
        self.product = Product.objects.create(
            product_id=1,
            seller=self.seller,
            category=self.category,
            product_name='Test Product',
            price=10000,
            description='This is a test product.',
            is_visible=True,
            stock=50,
            discount_rate=0.10,
            is_option=True
        )

        # 주문 객체 생성
        self.order = Order.objects.create(
            order_id=1,
            customer=self.customer,
            order_date=date.today(),
            order_status='결제완료',
            shipping_address='Test Address',
            postal_code='12345',
            recipient='Test Recipient',
            recipient_phone_number='01012345678',
            payment_method='신용카드'
        )

        # 결제 정보 객체 생성
        self.payment = Payment.objects.create(
            payment_id=1,
            order=self.order,
            paid_amount=10000,  # 결제 금액
            imp_uid='imp_uid_test',
            merchant_uid='merchant_uid_test'
        )

        # # API 클라이언트 인스턴스 생성
        # self.client = APIClient()

        # 장바구니 추가 URL
        self.cancel_order_url = reverse('customer:cancel_order')

        # RequestFactory 인스턴스 생성
        self.factory = RequestFactory()

        # cart와 cartitem 생성

    def test_cancel_order_authenticated(self):
        # 인증된 고객으로 로그인 상태를 설정합니다.
        self.client.login(username=self.customer.username, password=self.customer.password)

        # POST 요청 보낼 데이터 준비
        data = {}






        # API의 URL Reverse
        url = reverse('cancel_order', args=[self.order.order_id])

        # POST 요청 보낼 데이터 준비
        data = {}

        # POST 요청 보내기
        response = self.client.post(url, data, format='json')

        # 응답 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 주문 상태가 '환불완료'로 변경되었는지 확인
        updated_order = Order.objects.get(order_id=self.order.order_id)
        self.assertEqual(updated_order.order_status, '환불완료')

        # 추가적으로 필요한 응답 데이터에 대한 확인은 상황에 따라 추가할 수 있습니다.
