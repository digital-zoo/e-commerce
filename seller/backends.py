from django.contrib.auth.backends import ModelBackend
from .models import Seller

class SellerAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            seller = Seller.objects.get(username=username)
            if seller.check_password(password):
                return seller
        except Seller.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Seller.objects.get(pk=user_id)
        except Seller.DoesNotExist:
            return None