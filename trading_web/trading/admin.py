# trading/admin.py
from django.contrib import admin
from .models import TradingAccount, Trade, Message

admin.site.register(TradingAccount)
admin.site.register(Trade)
admin.site.register(Message)
