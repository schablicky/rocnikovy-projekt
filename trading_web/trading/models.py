from django.db import models
from django.contrib.auth.models import User

class TradingAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    is_demo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Trade(models.Model):
    TRADE_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell')
    ]
    account = models.ForeignKey(TradingAccount, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    entry_price = models.DecimalField(max_digits=10, decimal_places=5)
    exit_price = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    is_ai_generated = models.BooleanField(default=False)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
