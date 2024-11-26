# trading/urls.py
from django.urls import path
from . import views

app_name = 'trading'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('ai-trading/', views.ai_trading, name='ai_trading'),
    path('manual-trading/', views.manual_trading, name='manual_trading'),
    path('copy-trading/', views.copy_trading, name='copy_trading'),
    path('messages/', views.messages_view, name='messages'),
    path('api/execute-trade/', views.execute_trade, name='execute_trade'),
]