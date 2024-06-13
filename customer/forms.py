from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Membership  

User = get_user_model()

class SignupForm(UserCreationForm):
    username = forms.CharField(required=True,label="아이디")
    email = forms.EmailField(required=True,label="이메일")
    phone_number = forms.CharField(required=True,label="휴대폰 번호")
    
    membership_id = forms.CharField(required=True, widget=forms.HiddenInput())  # HiddenInput 위젯을 사용합니다.
    customer_name = forms.CharField(required=True,label="이름")
    address = forms.CharField(required=False,label="주소(필수X)")
    postal_code = forms.CharField(required=False,label="우편번호(필수X)")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'phone_number', 'customer_name', 'address', 'postal_code',)
    
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['membership_id'].initial = 1  # 기본값을 여기서 설정합니다.
    
    def save(self, commit=True):
        user = super().save(commit=False)
        membership_id = self.cleaned_data.get('membership_id', 1)  # 폼에서 membership_id 값을 가져옵니다.
        membership = Membership.objects.get(pk=membership_id)  # membership_id를 이용해 Membership 객체를 조회합니다.
        user.membership = membership  # 조회한 Membership 객체를 user의 membership 필드에 할당합니다.
        if commit:
            user.save()
        return user
    
from django import forms
from django.core.validators import MinValueValidator

class CartItemForm(forms.Form):
    quantity = forms.IntegerField(validators=[MinValueValidator(1)])