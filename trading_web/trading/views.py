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
from .services.trade_service import execute_trade, close_trade
import asyncio
from django.shortcuts import redirect
from .forms import UserSettingsForm
from rest_framework import status
from rest_framework.response import Response
from .models import CustomUser, Trade, News, MarketData, Message
import logging
from .services.market_data_service import fetch_and_save_market_data
from django.utils import timezone
import requests
from .forms import MessageForm, NewChatForm
from django.db.models import Q


def home(request):
    return render(request, 'home.html')

def leaderboards(request):
    users = CustomUser.objects.all().order_by('-balance')
    return render(request, 'leaderboards.html', {'users': users})

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

@login_required(login_url='/registration/login/')
def dashboard(request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        market_data = MarketData.objects.all().order_by('-id')[:100]
        market_data_list = [{
            'time': m.time.isoformat(),
            'close': float(m.close),  # Ensure numbers are serializable
            'symbol': m.symbol
        } for m in market_data]
        
        recent_trades = Trade.objects.filter(user=request.user).select_related('user').order_by('-time')[:5]
        
        today = datetime.today().date()
        dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
        trade_counts = Trade.objects.filter(time__date__gte=today - timedelta(days=6)).values('time__date').annotate(count=Count('id')).order_by('time__date')
        
        trade_dict = {trade['time__date']: trade['count'] for trade in trade_counts}
        
        now = timezone.now()
        last_100_minutes = now - timedelta(minutes=100)
        market_data = MarketData.objects.filter(time__gte=last_100_minutes).order_by('time')
        
        # Convert datetime objects to strings
        '''market_data_list = list(market_data.values('time', 'close'))
        for data in market_data_list:
            data['time'] = data['time'].isoformat()'''

        user = request.user
        if user.is_authenticated:
            url = f"https://mt-client-api-v1.london.agiliumtrade.ai/users/current/accounts/{user.metaid}/positions"
            headers = {
                "Accept": "application/json",
                "auth-token": user.apikey,
            }
            response = requests.get(url, headers=headers)
            open_trades = response.json() if response.status_code == 200 else []
        else:
            open_trades = []
        
        '''market_data_json = json.dumps(market_data_list)'''
        latest_news = News.objects.order_by('-publishdate')[:5]
        total_user_trades = Trade.objects.filter(user=request.user).count()
        return render(request, 'dashboard.html', {
            'market_data_json': json.dumps(market_data_list),
            'recent_trades': recent_trades,
            'latest_news': latest_news,
            'total_trades': total_user_trades,
            'open_trades': open_trades,
    })
        

logger = logging.getLogger(__name__)


@login_required
@api_view(['POST'])
def close_trade_view(request):
    user = request.user
    position_id = request.data.get('positionId')
    
    if not user.apikey or not user.metaid:
        return Response({'error': 'MetaAPI credentials not provided'}, status=400)
    
    try:
        result = close_trade(user, position_id)
        return Response({'success': True, 'result': result}, status=200)
    except Exception as e:
        if 'UnauthorizedError' in str(e):
            return Response({'error': 'Invalid API Key. Please update your API Key in the user settings.'}, status=401)
        return Response({'error': str(e)}, status=500)

@login_required
@api_view(['POST'])
def execute_trade_view(request):
    user = request.user
    symbol = request.data.get('symbol')
    trade_type = request.data.get('trade_type')
    logger.info(request.data.get('trade_type'))
    volume = float(request.data.get('volume'))
    
    if not user.apikey or not user.metaid:
        return Response({'error': 'MetaAPI credentials not provided'}, status=400)
    
    try:
        result = execute_trade(user, symbol, trade_type, volume)
        return Response({'success': True, 'result': result}, status=200)
    except Exception as e:
        if 'UnauthorizedError' in str(e):
            return Response({'error': 'Invalid API Key. Please update your API Key in the user settings.'}, status=401)
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


@login_required
@api_view(['GET'])
def fetch_and_save_market_view(request):
    user = request.user
    logger.info(request.data.get('trade_type'))
    
    if not user.apikey or not user.metaid:
        return Response({'error': 'MetaAPI credentials not provided'}, status=400)
    
    try:
        result = fetch_and_save_market_data(user)
        return Response({'success': True, 'result': result}, status=200)
    except Exception as e:
        if 'UnauthorizedError' in str(e):
            return Response({'error': 'Invalid API Key. Please update your API Key in the user settings.'}, status=401)
        return Response({'error': str(e)}, status=500)


@login_required
def message_list(request):
    received_messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    sent_messages = Message.objects.filter(sender=request.user).order_by('-timestamp')
    return render(request, 'chats/message_list.html', {'received_messages': received_messages, 'sent_messages': sent_messages})

@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('message_list')
    else:
        form = MessageForm()
    return render(request, 'chats/send_message.html', {'form': form})

@login_required
def chat_list(request):
    existing_chats = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).values('sender', 'receiver').distinct()
    
    chat_users = set()
    for chat in existing_chats:
        if chat['sender'] != request.user.id:
            chat_users.add(chat['sender'])
        if chat['receiver'] != request.user.id:
            chat_users.add(chat['receiver'])
    
    chat_users = CustomUser.objects.filter(id__in=chat_users)
    
    if request.method == 'POST':
        form = NewChatForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                other_user = CustomUser.objects.get(username=username)
                return redirect('trading:chat_detail', user_id=other_user.id)
            except CustomUser.DoesNotExist:
                form.add_error('username', 'User does not exist')
    else:
        form = NewChatForm()
    
    return render(request, 'chats/chat_list.html', {'users': chat_users, 'form': form})

@login_required
def chat_detail(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)
    messages = Message.objects.filter(
        Q(sender=request.user) & Q(receiver=other_user) |
        Q(sender=other_user) & Q(receiver=request.user)
    ).order_by('timestamp')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = other_user
            message.save()
            return redirect('trading:chat_detail', user_id=user_id)
    else:
        form = MessageForm()

    return render(request, 'chats/chat_detail.html', {'other_user': other_user, 'messages': messages, 'form': form})


@login_required
@api_view(['GET'])
def update_balance_view(request):
    user = request.user
    
    if not user.apikey or not user.metaid:
        return Response({'error': 'MetaAPI credentials not provided'}, status=400)
    
    url = f"https://mt-client-api-v1.london.agiliumtrade.ai/users/current/accounts/{user.metaid}/account-information"
    headers = {
        "Accept": "application/json",
        "auth-token": user.apikey,
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            account_info = response.json()
            user.balance = account_info['balance']
            user.save()
            return Response({'success': True, 'balance': user.balance}, status=200)
        else:
            return Response({'error': 'Failed to fetch account information'}, status=response.status_code)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
def chart_view(request):
    # Načítání dat EURUSD z databáze
    market_data = MarketData.objects.filter(symbol="EURUSD").order_by('time')
    
    labels = [data.time.strftime('%Y-%m-%d %H:%M:%S') for data in market_data]
    dataset = [[data.open, data.close] for data in market_data]

    context = {
        'labels': labels,
        'dataset': dataset,
    }
    return render(request, 'chart.html', context)

def aistats(request):
    context = {
        'page_title': 'AI Trading Statistics'
    }
    return render(request, 'aistats.html', context)
    
