from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import datetime

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    demo_balance = models.DecimalField(max_digits=15, decimal_places=2, default=10000)
    meta_api_token = models.CharField(max_length=255, blank=True)
    account_id = models.CharField(max_length=100, blank=True)
    is_demo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

class TradingPair(models.Model):
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.symbol

class Trade(models.Model):
    TRADE_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell')
    ]
    
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=TRADE_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    entry_price = models.DecimalField(max_digits=15, decimal_places=5)
    exit_price = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    is_demo = models.BooleanField(default=True)
    is_ai_trade = models.BooleanField(default=False)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    profit_loss = models.DecimalField(max_digits=15, decimal_places=2, null=True)

class AIModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE)
    accuracy = models.FloatField(default=0)
    total_trades = models.IntegerField(default=0)
    profitable_trades = models.IntegerField(default=0)
    last_trained = models.DateTimeField(auto_now=True)
    model_path = models.CharField(max_length=255)
    
    def win_rate(self):
        return (self.profitable_trades / self.total_trades * 100) if self.total_trades > 0 else 0

class CopyTrading(models.Model):
    follower = models.ForeignKey(UserProfile, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(UserProfile, related_name='followers', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    copy_amount_percentage = models.IntegerField(
        validators=[MinValueValidator(1)],
        default=100
    )
    started_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class MarketData(models.Model):
    pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    open = models.DecimalField(max_digits=15, decimal_places=5)
    high = models.DecimalField(max_digits=15, decimal_places=5)
    low = models.DecimalField(max_digits=15, decimal_places=5)
    close = models.DecimalField(max_digits=15, decimal_places=5)
    volume = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['pair', 'timestamp'])
        ]
