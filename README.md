# e-commerce
## 브랜치 정보
## user_test(송용진) : 유저 관련 기능
## seller-jaeheon(양재헌) : 구매자 관련 기능
## payment-dev(김연희) : 구매자 관련 기능
## cart(이승희) : 장바구니 기능
## LGM(이경민) : 판매자 관련 기능
1. 상품 등록
![alt text](image.png)

2. 등록한 상품 리스트
![alt text](image-1.png)

3. 상품 수정(내용 및 이미지 추가, 삭제)
![alt text](image-2.png)
![alt text](image-3.png)

4. 구매자 주문 시 주문 목록
 ![alt text](image-4.png)

## 양재헌
1. base.html,home.html 등 기본 html작성
![대체 텍스트](ReadmeImages/site_sample1.png)
2. 첫 화면에 보이는 상품들 정렬
![대체 텍스트](ReadmeImages/site_sample3.png)
3. 카테고리에 따라 상품들 분류
4. 할인율순,주문순,좋아요순으로 특정 기준으로 상품들 정렬
5. 하트 이미지와 함께 좋아요 기능을 구현
![대체 텍스트](ReadmeImages/site_sample2.png)
6. 검색기능
![대체 텍스트](ReadmeImages/site_sample4.png)

## 송용진
**1.사용자 정의 User 테이블**
AbstractBaseUser를 상속받아 구매자, 판매자 테이블의 공통 필드를 가지고 있는  (뼈대 역할)MyUser 테이블을 1차적으로 만들고 이를 상속받는 구매자 테이블인 Customer,  판매자 테이블인 Seller를 각각 만들었습니다. 결과적으로 만든 사용자 정의 User 테이블은 총 3개이고, 로그인에 사용되는 사용자 정의 User 테이블은 Customer와 Seller테이블입니다.

**2.Customer를 테이블을 이용한 구매자 인증과 로그인**
config/settings.py
…
AUTH_USER_MODEL = 'customer.Customer'
…
이와 같이 설정을 통해 
Customer 테이블을 기준으로
django 내장 authenticate, login, logout 함수를 사용하여 
편리하게 로그인 및 로그아웃 기능을 구현할 수 있었습니다.

**3.Seller 테이블을 이용한 판매자 인증과 로그인**
이미 AUTH_USER_MODEL을 Customer 테이블로 설정하였고,
Seller 테이블도 AUTH_USER_MODEL에 추가하고 싶었지만,
AUTH_USER_MODEL은 1개만 설정할 수 있기 때문에
Seller 테이블을 이용한 인증 기능은 
seller/backends.py에서 SellerAuthenticationBackend 클래스를 통해 
Django의 인증 시스템을 확장하여 구현하였습니다.

SellerAuthenticationBackend 클래스는 ModelBackend를 상속받아,
authenticate 메소드를 오버라이드하여 
사용자 이름과 비밀번호를 확인하는 방식입니다.

seller/views.py
...
login(request, seller, backend='seller.backends.SellerAuthenticationBackend')
...
이와 같이 판매자 로그인 처리는 커스텀 백엔드를 사용하여 수행되며, 
아이디, 패스워드가 Seller 테이블 정보와 일치하는 사용자일 경우 로그인할 수 있도록
django의 login 함수를 통해 사용자 로그인 기능을 구현했습니다.

django의 authenticate 함수가 커스텀 백엔드를 사용할 수 있게
config/settings.py
…
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', # 기본 인증 백엔드
    'seller.backends.SellerAuthenticationBackend', # Seller 인증 백엔드
]
…
이와 같이 settings.py 파일의 AUTHENTICATION_BACKENDS 설정에 추가했습니다.