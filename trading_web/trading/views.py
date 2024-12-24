import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CustomUser, Trade, MarketData, News
from .services.trade_service import execute_trade
from django.db.models import Count
from datetime import datetime, timedelta
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
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .services.trade_service import execute_trade
import asyncio
from django.shortcuts import redirect
from .forms import UserSettingsForm
from rest_framework import status
from rest_framework.response import Response
from .models import CustomUser, Trade, News, MarketData

def home(request):
    return render(request, 'home.html')

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

    recent_trades = Trade.objects.select_related('user').order_by('-time')[:5]
    
    
    today = datetime.today().date()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    trade_counts = Trade.objects.filter(time__date__gte=today - timedelta(days=6)).values('time__date').annotate(count=Count('id')).order_by('time__date')
    
    
    trade_dict = {trade['time__date']: trade['count'] for trade in trade_counts}
    
   
    chart_labels = [date.strftime('%a') for date in dates] 
    chart_data = [trade_dict.get(date, 0) for date in dates]
    
    context = {
        'recent_trades': recent_trades,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'total_trades': Trade.objects.count(),
        'latest_news': News.objects.order_by('-publishdate')[:3],
    }
    return render(request, 'dashboard.html', context)

@login_required
@api_view(['POST'])
def execute_trade_view(request):
    user = request.user
    symbol = request.data.get('symbol')
    trade_type = request.data.get('trade_type')
    volume = float(request.data.get('volume'))
    take_profit = request.data.get('takeProfit')
    
    if not user.apikey or not user.metaid:
        return Response({'error': 'MetaAPI credentials not provided'}, status=400)
    
    try:
        result = execute_trade(user, symbol, trade_type, volume, take_profit)
        return Response({'success': True, 'result': result}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@login_required
def user_settings(request):
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserSettingsForm(instance=request.user)
    
    return render(request, 'user_settings.html', {'form': form})

