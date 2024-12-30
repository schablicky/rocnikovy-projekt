# trading/services/market_data_service.py
from metaapi_cloud_sdk import MetaApi
import asyncio
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
import logging
import random
import time

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
                
                
            # Add delay between chunks
            await asyncio.sleep(2)
        
        logger.info(f"Total successful candles: {len(successful_candles)}")
        logger.info(f"Total failed timestamps: {len(failed_timestamps)}")
            
    except Exception as e:
        logger.error(f"Fatal error in data fetching: {e}")
        if hasattr(e, 'details'):
            logger.error(f"Error details: {e.details}")
        raise

def update_market_data():
    try:
        api = MetaApi(settings.META_API_TOKEN)
        account = api.metatrader_account_api.get_account(settings.ACCOUNT_ID)
        account.wait_connected()

        connection = account.get_rpc_connection()
        connection.connect()

        timestamp = int(datetime.now().timestamp())
        candle = connection.get_candle(
            'EURUSD',  # symbol
            '1m',      # timeframe
            timestamp  # time
        )


    except Exception as e:
        logger.error(f"Error updating market data: {e}")

import requests
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

def fetch_and_save_market_data():
    try:
        url = f"https://mt-client-api-v1.london.agiliumtrade.ai/users/current/accounts/5a6f2a7e-8d92-4bb2-a2a1-a1ee576b951c/symbols/EURUSD/current-candles/1m"  # Replace with the actual API endpoint
        headers = {
            "Accept": "application/json",
            "auth-token": "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiIzNmNmNTVjZDQyZDEyZTIyMDdiMWUxMmZkZTY5NjM5YiIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiYWNjb3VudDokVVNFUl9JRCQ6NWE2ZjJhN2UtOGQ5Mi00YmIyLWEyYTEtYTFlZTU3NmI5NTFjIl19LHsiaWQiOiJtZXRhYXBpLXJlc3QtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyJhY2NvdW50OiRVU0VSX0lEJDo1YTZmMmE3ZS04ZDkyLTRiYjItYTJhMS1hMWVlNTc2Yjk1MWMiXX0seyJpZCI6Im1ldGFhcGktcnBjLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbImFjY291bnQ6JFVTRVJfSUQkOjVhNmYyYTdlLThkOTItNGJiMi1hMmExLWExZWU1NzZiOTUxYyJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbImFjY291bnQ6JFVTRVJfSUQkOjVhNmYyYTdlLThkOTItNGJiMi1hMmExLWExZWU1NzZiOTUxYyJdfSx7ImlkIjoibWV0YXN0YXRzLWFwaSIsIm1ldGhvZHMiOlsibWV0YXN0YXRzLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyJhY2NvdW50OiRVU0VSX0lEJDo1YTZmMmE3ZS04ZDkyLTRiYjItYTJhMS1hMWVlNTc2Yjk1MWMiXX0seyJpZCI6InJpc2stbWFuYWdlbWVudC1hcGkiLCJtZXRob2RzIjpbInJpc2stbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiYWNjb3VudDokVVNFUl9JRCQ6NWE2ZjJhN2UtOGQ5Mi00YmIyLWEyYTEtYTFlZTU3NmI5NTFjIl19XSwiaWdub3JlUmF0ZUxpbWl0cyI6ZmFsc2UsInRva2VuSWQiOiIyMDIxMDIxMyIsImltcGVyc29uYXRlZCI6ZmFsc2UsInJlYWxVc2VySWQiOiIzNmNmNTVjZDQyZDEyZTIyMDdiMWUxMmZkZTY5NjM5YiIsImlhdCI6MTczNTMyMjg1MCwiZXhwIjoxNzQzMDk4ODUwfQ.RIrpggKmLsPxn0UHXD_JCrZpX5GBzSKU6jcb0dib2-ISXsHSzi5Xi-k7Ruw8jskIY4oMVz88M6ZPvnbZlV_MnSqubtg1ELXMsSZkh2C7vym2hS2uF1592pSp2eOT-YIjxUIhpUnTNQzbaHjCmI_o0oXVsOc-YlJyrqDOm6AN5TrAO3BpjRXsCCRP4X2pEbO4Op4keGwS_TDXS-Q-MseochSQGFH2xZNyO9_MTzQdg-aGCGmtXmrz6AccJ8Jn4BXWrdFqQD0NB_EV_Ao_KUw6q55-PHV4nyrdSBoejCOBOWfhEVGtnbG0WHD5S3_ROlq0Mk3Bon0uiGDG9sMAQ6WwnkpG1IwYJwHsnVH-eF6GXuEE39R7St0Hr_nlrf3nzJXii4ExKP07SuYBIvk1v3rB5pDA-KksIaYHExQL9XMmV5l9zXGUVliT2_sTmaOoiL2SbLuXJ1osN6YUK0FDaeW68gyTU2lB_pQgXl8rfHX7GLm4jcbFGc7wt9mN59qTo71AL8--TmKpGOI42AOabhUkCwgjMwhnhH23OlddNCKauwe3qnx5AQBDps5S3E-okhMEKmFc8hphlEFjTPfkib9vJcnbc8ETqoN9WfZHmburZ1EgdLKMVnIIgfpvLe7zcgudUa22OB6WB7NRyT7D_TjJ6vgzFXLZr5JkFOYrfcRs5a8",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        logger.info(f"API response data: {data}")


    except Exception as e:
        logger.error(f"Error fetching market data: {e}")