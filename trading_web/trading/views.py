# trading/views.py
from django.shortcuts import render
from .models import TradingPair, Trade, AIModel

def home(request):
    context = {
        'trading_pairs': TradingPair.objects.filter(is_active=True)[:5],
        'recent_trades': Trade.objects.select_related('pair').order_by('-opened_at')[:5],
        'ai_models': AIModel.objects.select_related('pair').all()[:3],
        'total_trades': Trade.objects.count(),
        'successful_trades': Trade.objects.filter(profit_loss__gt=0).count()
    }
    return render(request, 'home.html', context)