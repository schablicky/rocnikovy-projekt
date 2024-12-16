# trading/services/market_data_service.py
from metaapi_cloud_sdk import MetaApi
import asyncio
from datetime import datetime, timedelta
from django.utils import timezone
from trading.models import MarketData
from django.conf import settings
import logging
import random

logger = logging.getLogger(__name__)

async def fetch_historical_eurusd():
    try:
        api = MetaApi(settings.META_API_TOKEN)
        logger.info("Connecting to MetaAPI...")
        
        account = await api.metatrader_account_api.get_account(settings.ACCOUNT_ID)
        await account.wait_connected()
        
        connection = account.get_rpc_connection()
        await connection.connect()
        await connection.wait_synchronized()
        
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=10000)
        total_candles = []
        chunk_size = 50  # Smaller chunks
        max_retries = 5  # More retries
        
        logger.info(f"Fetching historical data from {start_time} to {end_time}")
        
        async def fetch_with_backoff(timestamp, retry=0):
            try:
                # Add jitter to avoid thundering herd
                await asyncio.sleep(random.uniform(0.1, 0.5) * (2 ** retry))
                return await connection.get_candle(
                    'EURUSD',  # Changed from EUR/USD
                    '1m',
                    timestamp
                )
            except Exception as e:
                if retry < max_retries:
                    return await fetch_with_backoff(timestamp, retry + 1)
                raise e

        successful_candles = []
        failed_timestamps = []
        
        for i in range(0, 10000, chunk_size):
            chunk_candles = []
            chunk_start = start_time + timedelta(minutes=i)
            
            for j in range(chunk_size):
                current_time = chunk_start + timedelta(minutes=j)
                timestamp = int(current_time.timestamp())
                
                try:
                    candle = await fetch_with_backoff(timestamp)
                    if candle:
                        chunk_candles.append(candle)
                except Exception as e:
                    failed_timestamps.append(timestamp)
                    logger.error(f"Failed to fetch candle at {current_time}: {e}")
            
            if chunk_candles:
                successful_candles.extend(chunk_candles)
                logger.info(f"Successfully fetched {len(chunk_candles)} candles in chunk")
                
                # Save chunk to database
                objects = [
                    MarketData(
                        symbol='EURUSD',
                        price=candle['close'],
                        openprice=candle['open'],
                        closeprice=candle['close'],
                        volume=candle['volume'],
                        timestamp=timezone.make_aware(datetime.fromtimestamp(candle['time']))
                    ) for candle in chunk_candles
                ]
                MarketData.objects.bulk_create(objects)
                
            # Add delay between chunks
            await asyncio.sleep(2)
        
        logger.info(f"Total successful candles: {len(successful_candles)}")
        logger.info(f"Total failed timestamps: {len(failed_timestamps)}")
            
    except Exception as e:
        logger.error(f"Fatal error in data fetching: {e}")
        if hasattr(e, 'details'):
            logger.error(f"Error details: {e.details}")
        raise

async def update_market_data():
    try:
        api = MetaApi(settings.META_API_TOKEN)
        account = await api.metatrader_account_api.get_account(settings.ACCOUNT_ID)
        await account.wait_connected()
        
        connection = account.get_rpc_connection()
        await connection.connect()
        
        while True:
            try:
                timestamp = int(datetime.now().timestamp())
                candle = await connection.get_candle(
                    'EURUSD',  # symbol
                    '1m',      # timeframe
                    timestamp  # time
                )
                
                if candle:
                    MarketData.objects.create(
                        symbol='EURUSD',
                        price=candle['close'],
                        openprice=candle['open'],
                        closeprice=candle['close'],
                        volume=candle['volume'],
                        timestamp=timezone.make_aware(datetime.fromtimestamp(candle['time']))
                    )
                
                await asyncio.sleep(60)  # Wait 1 minute before next update
                
            except Exception as e:
                logger.error(f"Error updating market data: {e}")
                await asyncio.sleep(60)  # Wait before retry
                
    except Exception as e:
        logger.error(f"Connection error: {e}")
        raise