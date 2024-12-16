# trading/management/commands/fetch_forex_data.py
from django.core.management.base import BaseCommand
import asyncio
from trading.services.market_data_service import fetch_historical_eurusd, update_market_data

class Command(BaseCommand):
    help = 'Fetches historical EURUSD data and starts live updates'

    def handle(self, *args, **kwargs):
        self.stdout.write('Fetching historical data...')
        asyncio.run(fetch_historical_eurusd())
        self.stdout.write('Starting live updates...')
        asyncio.run(update_market_data())