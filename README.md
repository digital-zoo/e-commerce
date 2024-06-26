# e-commerce
## 브랜치 정보
## user_test(송용진) : 유저 관련 기능
## seller-jaeheon(양재헌) : 구매자 관련 기능
## payment-dev(김연희) : 구매자 관련 기능
## cart(이승희) : 장바구니 기능
처음 계획했던 목표들은 3가지였습니다.

- AJAX 이용한 비동기 처리
- 장바구니에서 상품 옵션 수정
- 세션 기반 장바구니

AJAX를 이용한 비동기 처리를 통해 페이지의 새로고침없이 서버와 데이터를 주고 받으며 상품의 수량을 변경하거나 삭제할 수 있었습니다.

삭제 버튼을 예시로 설명하자면, 장바구니 상세 페이지에선 '삭제' 버튼을 제공합니다. 이 버튼은 jQuery를 이용해 클릭 이벤트에 연결되어 있습니다. 해당 버튼을 클릭하면 AJAX 요청이 서버로 전송됩니다. 요청 안에는 요청을 보낼 URL, Http 메서드, 데이터 타입, 상품의 ID, CSRF 토큰이 있습니다. 서버에서는 이 요청을 받아 해당 상품을 장바구니에서 삭제하고, 성공적으로 처리되었음을 알립니다. 이 후 HTML에서 해당 항목을 제거하고 관련 가격 내용을 업데이트합니다. 

웹 페이지의 반응성을 높이고, 유저와 웹 페이지의 자연스러운 상호작용을 통해 사용자 경험을 향상시킬 수 있었습니다.

아쉽게도, 세션 기반 장바구니는 성공하지 못했습니다. 이는 3차 프로젝트에서 다룰 예정입니다. 

장바구니의 상품이 삭제되거나 수량이 변경될 때 가격이 예상대로 업데이트되지 않았습니다. 또한, 비로그인 시에 사용하던 세션 장바구니의 데이터를 로그인 후에도 동일하게 사용하기 위해선 세션에 데이터를 어떤 형태(데이터 구조)로 넣을지 고민해야 했지만 시간 관계상 다음 프로젝트로 미뤄야 했습니다.


1. 장바구니에 상품 담기
<br>

![put](https://github.com/digital-zoo/e-commerce/assets/162934058/536a6b64-62f3-4cf1-8b68-0d6fe143f945)
<br>

2. 장바구니에서 상품 삭제
<br>

![delete](https://github.com/digital-zoo/e-commerce/assets/162934058/b2ce4c06-9b22-469e-9228-3dea9e7df638)
<br>

3. 장바구니에서 수량 변경
<br>

![changequantity](https://github.com/digital-zoo/e-commerce/assets/162934058/3c912a57-db44-420d-a083-6c15a4bbffa8)
<br>

4. 2번과 3번에 따른 가격 변경

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

## 3차 프로젝트 추가 및 변경 사함
1. 상담 챗봇 추가
![alt text](image-7.png)
RAG(Retrieval-Augmented Generation 검색증강생성)를 이용해 쇼핑몰 db에 접근하여 사용자의 질문에 알맞는 대답을 하는 챗봇 구현
프롬프팅을 이용해 대답의 정확도 및 대답 방식 설정


2. 기존 코드 개선 사항
### 2-1 주문 목록 로딩 속도 개선
 기존에는 주문 목록을 호출하는 쿼리의 효율이 좋지않아 반복해서 같은 내용에 접근하여 데이터가 조금만 많아져도 속도가 현저히 느려졌지만 db 접근을 최소화 하고 상품과 연관된 데이터를 효율적으로 가져옴 (prefetch_related, Prefetch  이용)
### 2-2 상품 수정 시 url 입력으로 인한 접근 권한 오류
 기존에는 url 입력으로 자신이 등록하지 않은 상품도 등록이 가능 했던 것을 자신이 등록한 상품만 수정 가능하게 변경
![alt text](image-6.png)



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

## 김연희
---
### 1. 상품 상세보기 페이지
![상세상세페이지](ReadmeImages/상품상세페이지.jpg)
#### 할인
- 할인 없는 상품 : 상품 가격 출력
- 할인 있는 상품 : 할인가 및 할인율 안내

#### 재고확인
수량 버튼(-,+)은 1개부터 상품재고 수량 내에서만 활성화 됨

#### 제품 이미지
- 제품 사진 자동으로 넘어감
- 사진 하단의 바 또는 사진 좌우를 클릭하여 상품 사진 전환 가능

---
### 2. 상품 구매/결제 페이지
! 로그인하지 않은 사용자가 바로구매를 누르면 로그인 화면이 나오고, 그 후 자동으로 주문페이지로 넘어감

#### 전화번호 유효성 검사
![대체 텍스트](ReadmeImages/주문서_카트.png)

#### 주소검색 및 자동입력
배송 정보란에 구매자의 정보가 기본값으로 들어가 있음
![대체 텍스트](ReadmeImages/우편주소찾기.jpg)

#### 결제 화면
![대체 텍스트](ReadmeImages/결제이니시스.jpg)

---
### 3. 주문/결제 처리 과정

- 고객이 주문서를 작성하고 주문하기 버튼을 누른 후 진행됨
- 각 단계가 하나의 트랜잭션임 (1,2,3 단계)
- 3단계의 상품 재고 수정 부분에서 동시성 처리함

| 단계 | 설명   | 성공후  주문상태 |실패 시나리오   | 실패후 주문상태    | 안내화면 | 
|------|--------|------------------|---------------|------------|-------------| 
| 1.   | 주문 정보를 데이터베이스에 저장 | 주문중         | <li>재고 부족 : 재고 부족 안내(알림창) <br><br> <li>데이터 오류 : 데이터 오류로 인한 주문실패 안내(알림창) |       | ![대체 텍스트](ReadmeImages/오더에러알림.jpg)<br><br>![대체 텍스트](ReadmeImages/주문실패디비문제.jpg) |
| 2.   | PG사 결제(KG이니시스) | 주문중         | <li>결제 오류 : 결제 실패 이유 안내(주문실패 페이지) | 결제실패 | ![대체 텍스트](ReadmeImages/결제실패사용자취소.jpg)  |
| 3.   | 결제 정보를 데이터베이스에 저장 & 상품 재고 수정 | 결제완료   | <li>재고 부족 : 재고 부족으로 인한 환불 안내(알림창) <br><br> <li>데이터 오류 : 데이터 오류로 인한 환불 안내(주문실패 페이지) | 환불대기  | ![대체 텍스트](ReadmeImages/결제재고부족.jpg)<br><br>![대체 텍스트](ReadmeImages/결제실패디비문제_환불안내.jpg) |
| 성공   | 주문/결제 정보 요약안내(주문 성공 페이지)  |     |             |       | ![대체 텍스트](ReadmeImages/결제성공.jpg)  |
---

### 주문/결제에 추가된 기능 
---
#### 1. 결제 취소 (Cancel Payment)
- **개요**: REST API의 Swagger 문서를 참고하여 결제 취소 기능을 구현
- **기능 상세**:
  - **단일 상품 구매 취소**: 
    - 구매한 상품이 하나인 경우, 전체 환불을 수행하고 주문 상태를 '환불완료'로 처리
  - **다중 상품 구매 취소**: 
    - 구매한 상품이 여러 개인 경우, 해당 아이템만 부분 환불하고 주문 상태를 '부분환불'로 처리
    - 주문 내 모든 상품이 환불/취소되면 주문 상태를 '환불완료'로 업데이트
- **코드 설명**:
  - IAMPORT API를 사용하여 결제 취소 요청을 보냄
  - API 호출 후 응답을 바탕으로 주문과 주문 항목의 상태를 업데이트
- **예시**
  - ![결제 취소 기능](ReadmeImages/주문내역.jpg)

  ---

#### 2. 배송지 저장 (Save Shipping Address)
- **개요**: 고객이 주문을 할 때 입력한 배송지를 저장하여 이후 주문 시 다시 사용
- **기능 상세**:
  - 고객이 주문을 완료하면 해당 배송지를 '배송지 목록'에 저장
  - 이후 주문 시 저장된 배송지 목록에서 선택할 수 있게 함
- **코드 설명**:
  - 주문이 완료될 때마다 배송지 정보를 데이터베이스에 저장
  - 주문 시 저장된 배송지를 불러와 사용자가 선택할 수 있음
- **예시**
  - ![배송지 저장 기능](ReadmeImages/배송지목록.jpg)
  ---

  
#### 3. 테스트 코드 (Test Code)
- **개요**: 결제 취소 API가 올바르게 작동하는지 확인하기 위해 테스트 코드를 작성
- **기능 상세**:
  - 결제 취소 API 호출 시, 올바른 응답을 반환하고 주문 상태가 적절히 업데이트되는지 확인
  - 다양한 시나리오를 테스트하여 코드의 신뢰성을 확보
- **코드 설명**:
  - Django의 TestCase를 사용하여 테스트 코드를 작성
  - 실제 API 호출을 통해 결제 취소 기능을 검증
  - 환불 성공, 실패 시나리오를 테스트

#### 추가 설명
- **결제 취소 테스트 코드**:
  - 실제 IAMPORT API를 사용하여 액세스 토큰을 발급받고 결제 취소 요청을 보냅니다.
  - 결제 취소 후, 주문과 주문 항목의 상태가 예상대로 변경되는지 확인합니다.
- **테스트 파일 위치**: `customer/tests.py`
- **테스트 명령어**:
  ```bash
  python manage.py test customer
  ```

**환경 변수**:
- PAYMENT_REST_API_KEY와 PAYMENT_REST_API_SECRET는 IAMPORT API 호출을 위한 필수 환경 변수입니다.
- .env 파일에 다음과 같이 설정합니다:
```bash
PAYMENT_REST_API_KEY=your_api_key
PAYMENT_REST_API_SECRET=your_api_secret
```
