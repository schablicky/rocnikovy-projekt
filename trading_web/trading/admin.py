from django.contrib import admin
from django.contrib import admin
from .models import *

admin.site.register([UserProfile, TradingPair, Trade, AIModel, 
                    CopyTrading, Message, MarketData])

