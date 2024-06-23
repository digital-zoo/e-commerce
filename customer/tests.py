from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from customer.models import Order, OrderItem
from seller.models import Product
from django.utils import timezone

class OrderTestCase(TestCase):
    def setUp(self):
        # 테스트용 유저 생성
        self.user = User.objects.create_user(username='testuser', password='12345')
        # 테스트용 상품 생성
        self.product = Product.objects.create(product_id='1', name='Test Product', stock=10, price=1000)
        # 테스트용 클라이언트 설정
        self.client = Client()
        self.client.login(username='testuser', password='12345')
        # 주문 URL 설정
        self.order_url = reverse('save_order')
        self.cancel_url = lambda order_id: reverse('order-cancel', args=[order_id])

    def test_save_order_success(self):
        response = self.client.post(self.order_url, {
            'product_id': self.product.product_id,
            'quantity': 2,
            'shipping_address': 'Test Address',
            'shipping_address_detail': 'Detail',
            'postal_code': '12345',
            'recipient': 'Test Recipient',
            'recipient_phone_number': '01012345678',
            'payment_method': 'card'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(OrderItem.objects.first().quantity, 2)

    def test_save_order_insufficient_stock(self):
        response = self.client.post(self.order_url, {
            'product_id': self.product.product_id,
            'quantity': 20,
            'shipping_address': 'Test Address',
            'shipping_address_detail': 'Detail',
            'postal_code': '12345',
            'recipient': 'Test Recipient',
            'recipient_phone_number': '01012345678',
            'payment_method': 'card'
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': False, 'message': '현재 상품의 재고가 충분하지 않습니다'})
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)

    def test_save_order_missing_fields(self):
        response = self.client.post(self.order_url, {
            'product_id': self.product.product_id,
            'quantity': 2,
            'shipping_address': 'Test Address',
            'shipping_address_detail': 'Detail',
            'postal_code': '12345',
            # 'recipient': 'Test Recipient',  # 필수 필드를 일부러 누락
            'recipient_phone_number': '01012345678',
            'payment_method': 'card'
        })
        self.assertEqual(response.status_code, 400)  # 필수 필드가 누락된 경우, 적절한 상태 코드를 반환해야 함

    def test_cancel_order(self):
        # Create order first
        order = Order.objects.create(
            customer=self.user,
            order_date=timezone.now(),
            order_status='주문중',
            shipping_address='Test Address Detail',
            postal_code='12345',
            recipient='Test Recipient',
            recipient_phone_number='01012345678',
            payment_method='card',
            imp_uid='imp_123456789'
        )
        OrderItem.objects.create(order=order, product=self.product, quantity=2)
        
        # Cancel order
        response = self.client.post(self.cancel_url(order.id), {'reason': '취소 요청'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.get(id=order.id).order_status, 'cancelled')
