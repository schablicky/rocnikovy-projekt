import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
from metaapi_cloud_sdk import MetaApi

class HistoricalDataLoader:
    def __init__(self, token: str, account_id: str):
        self.meta_api = MetaApi(token)
        self.account_id = account_id

    async def get_account(self):
        account = await self.meta_api.metatrader_account_api.get_account(self.account_id)
        if account.state != 'DEPLOYED':
            print('Deploying account...')
            await account.deploy()
        if account.connection_status != 'CONNECTED':
            print('Waiting for connection...')
            await account.wait_connected()
        return account

    async def load_data(self, symbol: str, start_time: datetime, 
                       end_time: datetime, timeframe: str = '1m') -> pd.DataFrame:
        try:
            account = await self.get_account()
            all_candles = []
            pages = 20  # Number of pages to fetch
            current_start = None

            print(f'Downloading historical data for {symbol}...')
            started_at = datetime.now()

            for i in range(pages):
                candles = await account.get_historical_candles(
                    symbol, 
                    timeframe, 
                    current_start
                )
                
                if not candles or len(candles) == 0:
                    break
                    
                print(f'Downloaded {len(candles)} candles for page {i+1}')
                all_candles.extend(candles)
                
                # Update start time for next page
                current_start = candles[0]['time']
                current_start = current_start.replace(minute=current_start.minute - 1)

            if not all_candles:
                raise ValueError("No historical data received")

            # Convert to DataFrame
            data = pd.DataFrame([{
                'time': candle['time'],
                'open': float(candle['open']),
                'high': float(candle['high']),
                'low': float(candle['low']),
                'close': float(candle['close']),
                'volume': float(candle['tickVolume'])
            } for candle in all_candles])

            print(f'Download completed in {(datetime.now() - started_at).total_seconds():.2f}s')
            return self._preprocess_data(data)

        except Exception as e:
            print(f"Error loading data: {e}")
            raise

        finally:
            if 'account' in locals():
                await account.undeploy()

    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        data['returns'] = data['close'].pct_change()
        data['volatility'] = data['returns'].rolling(window=20).std()
        data.dropna(inplace=True)
        return data