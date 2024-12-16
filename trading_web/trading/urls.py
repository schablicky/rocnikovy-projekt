from django.urls import path
from . import views

app_name = 'trading'

urlpatterns = [
    path('', views.home, name='home'),  # Root URL pattern
]