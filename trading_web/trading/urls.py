from django.urls import path
from . import views
from .views import update_balance_view

app_name = 'trading'

urlpatterns = [
    path('', views.home, name='home'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('messages/', views.message_list, name='message_list'),
    path('messages/send/', views.send_message, name='send_message'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chats/<int:user_id>/', views.chat_detail, name='chat_detail'),
    path('update-balance/', update_balance_view, name='update_balance'),
]