# chat/urls.py

from django.urls import path
from .views import chatbot_query, chat_view


urlpatterns = [
    path('query/', chatbot_query, name='chatbot_query'),
    path('', chat_view, name='chat_view'),
]
