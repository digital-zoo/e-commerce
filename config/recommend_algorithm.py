from seller.models import *
from customer.models import *
###############   
from django.views.generic.base import TemplateView
# auth 모듈에 없는 가입 처리용 뷰 UserCreateView와 UserCreateDoneTV 코딩
from django.views.generic import CreateView # 테이블에 새로운 레코드 생성하기 위해 필요한 폼 보여주고, 입력된 데이터를 레코드로 생성하는 뷰, 테이블 변경 처리 관련
from django.contrib.auth.forms import UserCreationForm # User 모델의 객체를 생성하기 위해 보여주는 폼
from django.urls import reverse_lazy # reverse_lazy : 함수 인자로 url패턴명을 받음
from customer.forms import SignupForm
from django.db.models import Count
import random
from django.core.cache import cache
import pandas as pd
from django.contrib.auth import get_user_model
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise_distances
import numpy as np

# from django.utils import timezone
# from datetime import timedelta

# def calculate_product_age(product):
#     return (timezone.now() - product.created_at).days

def get_popular_products(likes_weight=0.5, oreders_weight=1, carts_weight=0.6):
    # Step 1: Get the top 30 products by order count
    top_products = (
        Product.objects.annotate(order_count=Count('orderitem'))
        .order_by('-order_count')[:30]
    )

    # Step 2: Calculate the score for each product
    product_scores = []
    for product in top_products:
        likes_count = Like.objects.filter(product=product).count()
        orders_count = OrderItem.objects.filter(product=product).count()
        carts_count = CartItem.objects.filter(product=product).count()

        # Score calculation
        last_updated = product.updated_at if product.updated_at else product.created_at
        product_age = (timezone.now() - last_updated).days
        # score = (likes_count * a + orders_count * b + carts_count * c) / (product_age + 2)
        score = (likes_count * likes_weight + orders_count * oreders_weight + carts_count * carts_weight) / (product_age + 2)
        product_scores.append((product, score))

    # Step 3: Sort products by score and get the top 10
    top_10_products = sorted(product_scores, key=lambda x: x[1], reverse=True)[:10]

    # Return the top 10 products
    return [product for product, score in top_10_products]

def cf_products(user_id, user_product_matrix=0, user_similarity_df=0, num_recommendations=3, num_product=6):
    
    # 좋아요 데이터 추출
    likes = Like.objects.all().values('customer_id', 'product_id')
    like_df = pd.DataFrame.from_records(likes)
  
    # 사용자-상품 행렬 생성 (사용자가 좋아요한 상품에 1, 아닌 경우 0)
    user_product_matrix = like_df.pivot_table(index='customer_id', columns='product_id', aggfunc='size', fill_value=0)
    
    # 사용자 간 유사도 계산
    #코사인 유사도
    # user_similarity = cosine_similarity(user_product_matrix)
    # user_similarity_df = pd.DataFrame(user_similarity, index=user_product_matrix.index, columns=user_product_matrix.index) 

    #자카드계수
    similarity_matrix = 1 - pairwise_distances(user_product_matrix.to_numpy(), metric='jaccard')
    user_similarity_df = pd.DataFrame(similarity_matrix, index=user_product_matrix.index, columns=user_product_matrix.index)
    
    # 특정 사용자의 좋아요 데이터 추출
    user_likes = user_product_matrix.loc[user_id]
    
    # 유사 사용자들의 좋아요 데이터 추출
    num_recommendations=min(num_recommendations,(len(user_similarity_df[user_id])-1))
    similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:num_recommendations+1].index
    similar_users_likes = user_product_matrix.loc[similar_users]
        
    # 추천 점수 계산
    recommend_scores = similar_users_likes.mean(axis=0)
        
    # 사용자가 이미 좋아요한 상품은 제외
    recommend_scores = recommend_scores[user_likes == 0]
        
    # 점수가 높은 순으로 상품 추천
    recommend_products = recommend_scores.sort_values(ascending=False).head(num_recommendations).index
    
    if len(recommend_products)>=num_product:
        return Product.objects.filter(product_id__in=recommend_products)[:num_product]
    else:    
        return Product.objects.filter(product_id__in=recommend_products)



class MatrixFactorization:
    def __init__(self, R, K, alpha, beta, iterations):
        """
        R: 사용자-상품 평점 행렬 (user-item rating matrix)
        K: 잠재 요인 (latent factor)의 수
        alpha: 학습률 (learning rate)
        beta: 정규화 파라미터 (regularization parameter)
        iterations: 반복 횟수
        """
        self.R = R
        self.num_users, self.num_items = R.shape
        self.K = K
        self.alpha = alpha
        self.beta = beta
        self.iterations = iterations

    def train(self):
        # 사용자 및 상품 잠재 요인 행렬 초기화
        self.P = np.random.normal(scale=1./self.K, size=(self.num_users, self.K))
        self.Q = np.random.normal(scale=1./self.K, size=(self.num_items, self.K))

        #과적합 방지
        self.b_u = np.zeros(self.num_users)
        self.b_d = np.zeros(self.num_items)
        self.b = np.mean(self.R[self.R.nonzero()])

        # 학습 과정
        # self.training_process = []
        for i in range(self.iterations):
            self.sgd()
            # mse = self.mean_squared_error()
            # self.training_process.append((i, mse))
            # if (i+1) % 10 == 0:
            #     print("Iteration: %d ; error = %.4f" % (i+1, mse))

    def sgd(self):
        for i in range(self.num_users):
            for j in range(self.num_items):
                if self.R[i, j] > 0:
                    # 오차 계산
                    e = self.R[i, j] - self.predict(i, j)

                    # 사용자 및 상품 잠재 요인 업데이트

                    self.b_u[i] += self.alpha * (e-(self.beta * self.b_u[i]))
                    self.b_d[j] += self.alpha * (e-(self.beta * self.b_d[j]))
                    
                    self.P[i, :] += self.alpha * (2 * e * self.Q[j, :] - self.beta * self.P[i, :])
                    self.Q[j, :] += self.alpha * (2 * e * self.P[i, :] - self.beta * self.Q[j, :])

    def predict(self, i, j):
        prediction = self.b + self.b_u[i] + self.b_d[j] + np.dot(self.P[i, :], self.Q[j, :])
        return prediction

    def mean_squared_error(self):
        xs, ys = self.R.nonzero()
        predicted = self.full_matrix()
        error = 0
        for x, y in zip(xs, ys):
            error += pow(self.R[x, y] - predicted[x, y], 2)
        return np.sqrt(error)

    def full_matrix(self):
        return np.dot(self.P, self.Q.T)

def MatrixFactorization_train_model():

    customers = Customer.objects.all()
    products = Product.objects.all()
    reviews = Review.objects.all().values('customer_id','product_id','rating')
    
    user_map = {customer.id: i for i, customer in enumerate(customers)}
    item_map = {product.product_id: i for i, product in enumerate(products)}

    R = np.zeros((len(customers), len(products)))
    for review in reviews:
        R[user_map[review['customer_id']], item_map[review['product_id']]] = review['rating']

    mf = MatrixFactorization(R, K=2, alpha=0.2, beta=0.2, iterations=10)
    mf.train()

    # 인덱스에서 ID로 매핑하는 딕셔너리 생성
    reverse_user_map = {v: k for k, v in user_map.items()}
    reverse_item_map = {v: k for k, v in item_map.items()}

    # 매핑된 행렬 생성
    mapped_matrix = {}

    for user_index, row in enumerate(mf.full_matrix()):
        user_id = reverse_user_map[user_index]
        mapped_matrix[user_id] = {}
        for item_index, rating in enumerate(row):
            item_id = reverse_item_map[item_index]
            mapped_matrix[user_id][item_id] = rating
    return mapped_matrix


def mf_products(user_id):
    mf = MatrixFactorization_train_model()
    predicted_ratings = mf[user_id]

    item_ids = sorted(predicted_ratings, key=predicted_ratings.get, reverse=True)[:5]
    recommended_items = [Product.objects.get(product_id=i) for i in item_ids] 
    return recommended_items