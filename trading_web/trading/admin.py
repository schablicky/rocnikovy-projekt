from django.contrib import admin
from django.contrib import admin
from .models import *

admin.site.register([CustomUser, Trade, News, 
                    CopyTrader, Message, MarketData])

