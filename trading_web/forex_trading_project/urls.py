from django.contrib import admin
from django.urls import path, include
from oauth2_provider import urls as oauth2_urls
from django.contrib.auth import views as auth_views
from trading.views import RegisterView
from trading.views import home, dashboard
from trading.views import execute_trade_view
from trading.views import user_settings
from trading.views import close_trade_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('o/', include(oauth2_urls)),
    path('oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('trading/', include('trading.urls', namespace='trading')),
    path('accounts/', include('allauth.urls')),
    path('execute-trade/', execute_trade_view, name='execute_trade'),
    path('settings/', user_settings, name='user_settings'),
    path('close-trade/', close_trade_view, name='close_trade'),
]
