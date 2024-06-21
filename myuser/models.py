from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import EmailValidator
from django.core.validators import RegexValidator

# 1단계, user manager 정의
class MyUserManager(BaseUserManager):
    def create_user(self, username,email, phone_number,password=None,**extra_fields):
        """
        일반 사용자 생성
        """
        if not username:
            raise ValueError('Users must have a username')
        
        user = self.model(
            username=username, 
            email=email,
            phone_number=phone_number,
            **extra_fields,           
        )

        user.set_password(password)
        user.save(using=self._db) # self._db는 ( save() 메서드와 같은 ) 데이터베이스 작업에서 사용되는 데이터베이스 연결을 지정
        
        return user        

    def create_superuser(self, username,email, phone_number,password=None,**extra_fields):
        """
        슈퍼유저 생성
        """
        user = self.create_user(
            username,
            email=email,
            phone_number=phone_number,            
            password=password,
            **extra_fields,            
        )

        user.is_staff = True
        user.is_superuser = True        
        user.save(using=self._db)

        return user

phone_regex = RegexValidator(
    regex=r'^(01[016789]\d{7,8})$',
    message="휴대폰 번호 형식이 올바르지 않습니다."
)

# 2단계, MyUser 생성   
class MyUser(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=50,unique=True,validators=[EmailValidator(message="이미 등록된 이메일 주소입니다.")])
    phone_number = models.CharField(max_length=11,unique=True,validators=[phone_regex])
    is_staff = models.BooleanField(default=False)  # 관리자 사이트 접근 권한

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number']

    objects = MyUserManager()

    class Meta:
        abstract = True    

    def __str__(self):
        return self.username