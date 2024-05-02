from django.contrib.auth.backends import ModelBackend
from .models import Seller

class SellerAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:            
            user = Seller.objects.get(username=username)
            # 비밀번호 검증
            if user.check_password(password):
                return user
        except Seller.DoesNotExist:
            # 사용자가 존재하지 않으면 None 반환
            return None