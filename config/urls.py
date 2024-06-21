"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings#,include
from config.views import *
from config.views import UserCreateView, UserCreateDoneTV # 가입처리를 수행하는 뷰

app_name = "config"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(),name='home'), # 홈화면
    path('customer/', include('customer.urls')),
    path('accounts/', include('django.contrib.auth.urls')), # 장고의 인증 URLconf를 가져와서 사용
    path('accounts/register/', UserCreateView.as_view(), name='register'), # 계정 생성 URl, 인증 관련 URL 모두 accounts/로 시작하도록 통일
    path('accounts/register/done/', UserCreateDoneTV.as_view(), name='register_done'), # 계정 생성 완료 메세지를 보여주기 위한 URL
    path('seller/', include('seller.urls')),        
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
