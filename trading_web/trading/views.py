from django.shortcuts import render
from .models import User, Trade, News, MarketData

def home(request):
    context = {
        'users': User.objects.all()[:5],
        'recent_trades': Trade.objects.select_related('user').order_by('-time')[:5],
        'market_data': MarketData.objects.all()[:5],
        'total_trades': Trade.objects.count(),
        'latest_news': News.objects.order_by('-publishdate')[:3]
    }
    return render(request, 'home.html', context)