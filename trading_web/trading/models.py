from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

# Custom user model, přidává role, apikey, metaid, balance a theme k django User modelu
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('trader', 'Trader'),
        ('subscriber', 'Subscriber'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='trader')
    apikey = models.CharField(max_length=5000, blank=True, null=True)
    metaid = models.CharField(max_length=45, blank=True, null=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    THEME_CHOICES = (
        ('light', 'Light'),
        ('dark', 'Dark'),
    )
    theme = models.CharField(max_length=5, choices=THEME_CHOICES, default='light')
    class Meta:
        app_label = 'trading'

    def __str__(self):
        return self.username


# Messages model, využíván pro zprávy mezi uživateli
class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}"


# News model, využíván pro zobrazování novinek
class News(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=5000)
    source = models.CharField(max_length=45)
    publishdate = models.DateTimeField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="news")
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)

    class Meta:
        ordering = ['-publishdate']

    def __str__(self):
        return self.title


# MarketData model, díky kterému se zobrazují grafy
class MarketData(models.Model):
    symbol = models.CharField(max_length=10)
    timeframe = models.CharField(max_length=10)
    time = models.DateTimeField()
    brokerTime = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    tickVolume = models.IntegerField()
    spread = models.IntegerField()

    class Meta:
        ordering = ['-time']

    def __str__(self):
        return f"{self.symbol}: ${self.price}"


# Trade model, využíván pro zaznamenávání obchodů
class Trade(models.Model):
    TRADE_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="trades")
    symbol = models.CharField(max_length=10)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPE_CHOICES)
    time = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    volume = models.FloatField(blank=True, null=True)
    position_id = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        ordering = ['-time']

    def __str__(self):
        return f"{self.trade_type.capitalize()} {self.symbol} by {self.user.username}"


# CopyTrader model, dosud nevyužitý model, který by měl sloužit k kopírování obchodů
class CopyTrader(models.Model):
    publisher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="published_trades")
    subscriber = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="subscribed_trades")
    ratio = models.FloatField(validators=[MinValueValidator(0.0)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subscriber.username} copies {self.publisher.username} (ratio: {self.ratio})"
