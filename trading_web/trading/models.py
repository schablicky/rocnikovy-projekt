from django.db import models
from django.core.validators import MinValueValidator

# User model
class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('trader', 'Trader'),
        ('subscriber', 'Subscriber'),
    ]

    username = models.CharField(max_length=45, unique=True)
    email = models.EmailField(max_length=45, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    apikey = models.CharField(max_length=500, blank=True, null=True)
    metaid = models.CharField(max_length=45, blank=True, null=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


# Messages model
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    message = models.TextField(max_length=1000, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.user.username} at {self.timestamp}"


# News model
class News(models.Model):
    title = models.CharField(max_length=45)
    content = models.TextField(max_length=500)
    source = models.CharField(max_length=45)
    publishdate = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="news")
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)

    class Meta:
        ordering = ['-publishdate']

    def __str__(self):
        return self.title


# MarketData model
class MarketData(models.Model):
    symbol = models.CharField(max_length=10)
    price = models.FloatField(null=True, blank=True)
    openprice = models.FloatField(null=True, blank=True)
    closeprice = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.symbol}: ${self.price}"


# Trade model
class Trade(models.Model):
    TRADE_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trades")
    symbol = models.CharField(max_length=10)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPE_CHOICES)
    time = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()

    class Meta:
        ordering = ['-time']

    def __str__(self):
        return f"{self.trade_type.capitalize()} {self.symbol} by {self.user.username}"


# CopyTrader model
class CopyTrader(models.Model):
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="published_trades")
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscribed_trades")
    ratio = models.FloatField(validators=[MinValueValidator(0.0)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subscriber.username} copies {self.publisher.username} (ratio: {self.ratio})"
