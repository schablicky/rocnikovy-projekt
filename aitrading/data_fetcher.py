from metaapi_cloud_sdk import MetaApi
import pandas as pd
import asyncio
import os
from dotenv import load_dotenv
import aiohttp
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Zakomentováno, protože se nepoužívá
'''class DataFetcher:
    def __init__(self):
        load_dotenv()
        self.api = MetaApi(os.getenv('META_API_TOKEN'))
        self.account_id = os.getenv('ACCOUNT_ID')
        self.connection = None
        self.account = None
        
    async def connect(self):
        self.account = await self.api.metatrader_account_api.get_account(self.account_id)
        self.connection = self.account.get_streaming_connection()
        await self.connection.connect()
        
    async def get_price_data(self, symbol='EURUSD', timeframe='1m', bars=100):
        candles = await self.connection.get_candles(symbol, timeframe, bars)
        df = pd.DataFrame(candles)
        return df[['time', 'open', 'high', 'low', 'close', 'tickVolume']]
        
    async def get_positions(self):
        return await self.connection.get_positions()
        
    async def execute_trade(self, action_type, symbol, volume=1):
        try:
            result = await self.connection.create_market_buy_order(
                symbol=symbol,
                volume=volume
            ) if action_type == "ORDER_TYPE_BUY" else await self.connection.create_market_sell_order(
                symbol=symbol,
                volume=volume
            )
            return result
        except Exception as e:
            print(f"Trade execution error: {e}")
            return None
            
    async def close_position(self, position_id):
        try:
            result = await self.connection.close_position(position_id)
            return result
        except Exception as e:
            print(f"Position closing error: {e}")
            return None'''

# Třída pro komunikaci s MetaApi
class RestDataFetcher:
    def __init__(self):
        load_dotenv()
        self.base_url = "https://mt-client-api-v1.london.agiliumtrade.ai" # URL pro MetaApi
        self.auth_token = os.getenv('META_API_TOKEN') # Token pro autentizaci
        self.account_id = os.getenv('ACCOUNT_ID') # ID účtu (oboje z .env souboru)
        # Hlavičky pro API requesty
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'auth-token': self.auth_token
        }
        self.logger = logging.getLogger(__name__)

    # Získání aktuální svíčky, symbol je defaultně EURUSD, max_retries je počet pokusů při neúspěchu
    # Zde vzniká problém, že když se nepodaří získat svíčku ani po 3 pokusech, tak se vrátí None
    # a AI se nerozjede, protože nemá data a tato skutečnost není nikde ošetřena,
    # toto se stává pouze u incialiace, kdy se získává 10 svíček, při samotném běhu se AI
    # akorát nerozhodne, a čeká na další svíčku, což může způsobit, že AI mine vhodný okamžik
    # pro obchodování
    async def get_current_candle(self, symbol='EURUSD', max_retries=3):
        retry_count = 0
        while retry_count < max_retries:
            try:
                url = f"{self.base_url}/users/current/accounts/{self.account_id}/symbols/{symbol}/current-candles/1m"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status == 200: # Pokud je status 200, tak se vrátí data
                            data = await response.json()
                            return data
                        elif response.status == 404: # Pokud není dostupná svíčka, tak se počká 5 sekund a zkusí se to znovu
                            logger.warning(f"Candle not available, retry {retry_count + 1}/{max_retries}")
                            await asyncio.sleep(5)
                            retry_count += 1
                        else:
                            logger.error(f"API Error: {response.status}")
                            return None
            except Exception as e:
                logger.error(f"Request Error: {e}")
                retry_count += 1
                await asyncio.sleep(5)
        return None

    # Získání aktuálních pozic
    async def get_positions(self):
        url = f"{self.base_url}/users/current/accounts/{self.account_id}/positions"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200: # Pokud je status 200, tak se vrátí data
                        return await response.json()
                    return None
            except Exception as e:
                self.logger.error(f"Failed to get positions: {e}")
                return None

    # Provedení obchodu, action_type je typ obchodu (BUY/SELL), symbol je měnový pár, volume je objem obchodu
    async def execute_trade(self, action_type, symbol, volume=1):
        url = f"{self.base_url}/users/current/accounts/{self.account_id}/trade"
        payload = {
            "actionType": action_type,
            "symbol": symbol,
            "volume": volume
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200: # Pokud je status 200, tak se vrátí data
                        return await response.json()
                    return None
            except Exception as e:
                self.logger.error(f"Trade execution failed: {e}")
                return None

    # Uzavření pozice, position_id je ID pozice (získáno z get_positions)
    async def close_position(self, position_id):
        url = f"{self.base_url}/users/current/accounts/{self.account_id}/trade"
        payload = {
            "actionType": "POSITION_CLOSE_ID",
            "positionId": position_id
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200: # Pokud je status 200, tak se vrátí data
                        return await response.json()
                    return None
            except Exception as e:
                self.logger.error(f"Position closing failed: {e}")
                return None