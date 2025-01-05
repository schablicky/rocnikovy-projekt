from django.core.management.base import BaseCommand
from trading.models import MarketData
from django.utils import timezone
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Populates the database with random market data'

    def handle(self, *args, **options):
        start_date = timezone.make_aware(datetime(2024, 1, 1))
        
        for i in range(100):
            current_date = start_date + timedelta(minutes=i)
            broker_time = current_date.strftime("%Y-%m-%d %H:%M:%S")
            
            MarketData.objects.create(
                symbol="EURUSD",
                time=current_date,
                brokerTime=broker_time,
                open=random.uniform(1.05, 1.15),
                high=random.uniform(1.05, 1.15),
                low=random.uniform(1.05, 1.15),
                close=random.uniform(1.05, 1.15),
                tickVolume=random.randint(100, 1000),
                spread=random.randint(1, 10),
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully populated market data'))