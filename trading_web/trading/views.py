from django.shortcuts import render
from .models import CustomUser, Trade, News, MarketData
from oauth2_provider.views.generic import ProtectedResourceView
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.decorators import protected_resource
from rest_framework import viewsets
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.shortcuts import render, get_object_or_404
from .models import News
from .forms import CustomUserCreationForm

def home(request):
    context = {
        'users': CustomUser.objects.all()[:5],
        'recent_trades': Trade.objects.select_related('user').order_by('-time')[:5],
        'market_data': MarketData.objects.all()[:5],
        'total_trades': Trade.objects.count(),
        'latest_news': News.objects.order_by('-publishdate')[:3]
    }
    return render(request, 'home.html', context)

class ApiEndpoint(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'message': 'Hello, OAuth2!'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@protected_resource()
def protected_api(request):
    return JsonResponse({'data': 'This is protected data'})

class ProtectedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
   

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    return render(request, 'news_detail.html', {'news': news_item})
def dashboard(request):
    context = {
        'users': CustomUser.objects.all()[:5],
        'recent_trades': Trade.objects.select_related('user').order_by('-time')[:5],
        'market_data': MarketData.objects.all()[:5],
        'total_trades': Trade.objects.count(),
        'latest_news': News.objects.order_by('-publishdate')[:3]
    }
    return render(request, 'dashboard.html', context)