# trading/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class TradingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

    async def trading_update(self, event):
        await self.send(text_data=json.dumps(event))