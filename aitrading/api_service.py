from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging
import asyncio
import json

app = FastAPI(title="AI Trading Bot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state to store bot info
bot_state = {
    "model_state": {
        "epsilon": 1.0,
        "total_steps": 0,
    },
    "trading_stats": {
        "total_profit": 0,
        "trades_count": 0,
        "current_position": None,
    },
    "indicators": {
        "SMA": [],
        "RSI": [],
        "MACD": [],
    },
    "last_prediction": None
}

@app.get("/")
async def root():
    return {"status": "AI Trading Bot API is running"}

@app.get("/state")
async def get_state():
    return bot_state

@app.get("/model")
async def get_model_state():
    return bot_state["model_state"]

@app.get("/stats")
async def get_trading_stats():
    return bot_state["trading_stats"]

@app.get("/prediction")
async def get_last_prediction():
    return {"last_prediction": bot_state["last_prediction"]}

@app.get("/indicators")
async def get_indicators():
    return {"indicators": ["SMA", "RSI", "MACD"]}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send state every second
            await websocket.send_json({
                "model_state": {
                    "epsilon": 1.0,
                    "total_steps": 0
                },
                "trading_stats": {
                    "total_profit": 0,
                    "trades_count": 0
                },
                "indicators": {
                    "rsi": None,
                    "macd": None,
                    "sma": None,
                    "atr": None
                }
            })
            await asyncio.sleep(1)
    except:
        await websocket.close()

def start_api_server():
    uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    start_api_server()