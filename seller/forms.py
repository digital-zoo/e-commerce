from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Seller  # Seller 모델을 직접 참조

class SellerSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=True)

    company_name = forms.CharField(required=True)    
    business_contact = forms.CharField(required=False)
    registration_number = forms.CharField(required=True)
    # 필요한 추가 필드 정의

    class Meta:
        model = Seller  # Customer 모델 대신 Seller 모델을 사용
        fields = UserCreationForm.Meta.fields + ('email', 'phone_number', 'company_name','business_contact','registration_number',)
        # UserCreationForm.Meta.fields에 포함되지 않은 Seller 모델 특유의 필드를 추가

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']

        user.company_name = self.cleaned_data['company_name']
        user.company_name = self.cleaned_data['company_name']
        user.registration_number = self.cleaned_data['registration_number']
        # Seller 모델에 정의된 추가 필드 데이터를 저장
        if commit:
            user.save()
        return user