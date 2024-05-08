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
![put](https://github.com/digital-zoo/e-commerce/assets/162934058/536a6b64-62f3-4cf1-8b68-0d6fe143f945)
<br>
2. 장바구니에서 상품 삭제
![delete](https://github.com/digital-zoo/e-commerce/assets/162934058/b2ce4c06-9b22-469e-9228-3dea9e7df638)
<br>
3. 장바구니에서 수량 변경
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
