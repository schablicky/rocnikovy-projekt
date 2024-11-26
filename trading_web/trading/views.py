from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TradingAccount, Trade, Message
from rest_framework.decorators import api_view
from rest_framework.response import Response
import asyncio

# Import from installed package
from trading_ai import (
    ForexTradingEnvironment, 
    TradingAgent,
    get_current_market_data,
    get_current_price,
    Config
)

def home(request):
    return render(request, 'trading/home.html')

@login_required
def dashboard(request):
    account = TradingAccount.objects.get_or_create(user=request.user)[0]
    trades = Trade.objects.filter(account=account).order_by('-created_at')[:10]
    return render(request, 'trading/dashboard.html', {
        'account': account,
        'trades': trades
    })

@login_required
def ai_trading(request):
    return render(request, 'trading/ai_trading.html')

@login_required
def manual_trading(request):
    return render(request, 'trading/manual_trading.html')

@login_required
def copy_trading(request):
    return render(request, 'trading/copy_trading.html')

@login_required
def messages_view(request):
    received = Message.objects.filter(receiver=request.user).order_by('-created_at')
    sent = Message.objects.filter(sender=request.user).order_by('-created_at')
    return render(request, 'trading/messages.html', {
        'received': received,
        'sent': sent
    })

@api_view(['POST'])
@login_required
async def execute_trade(request):
    action = request.data.get('action')
    symbol = request.data.get('symbol')
    amount = request.data.get('amount')
    
    account = request.user.tradingaccount
    
    # Get AI prediction if needed
    env = ForexTradingEnvironment(get_current_market_data(), Config())
    agent = TradingAgent(env, Config())
    prediction = await agent.predict(symbol)
    
    # Execute trade
    trade = Trade.objects.create(
        account=account,
        symbol=symbol,
        trade_type=action,
        amount=amount,
        entry_price=get_current_price(symbol),
        is_ai_generated=False
    )
    
    return Response({'success': True, 'trade_id': trade.id})
