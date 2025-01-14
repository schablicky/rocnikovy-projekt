from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging
import asyncio
import json
import numpy as np
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Server pro získávání stavu modelu a indikátorů pro lepší debugování a vizualizaci
"""

app = FastAPI(title="AI Trading Bot API")

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

connected_clients = set()

def clean_for_json(obj):
    if isinstance(obj, dict):
        return {key: clean_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        return clean_for_json(obj.tolist())
    elif isinstance(obj, (np.float32, np.float64)):
        if np.isnan(obj) or np.isinf(obj):
            return 0.0
        return float(obj)
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
        return obj
    return obj

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return clean_for_json(obj)
        except:
            return str(obj)

class TradingJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.floating):
            if np.isnan(obj) or np.isinf(obj):
                return 0.0
            return float(obj)
        return super().default(obj)

@app.get("/")
async def root():
    return {"status": "AI Trading Bot API is running"}

@app.get("/state")
async def get_state():
    try:
        state_data = bot_state
        cleaned_data = clean_for_json(state_data)
        return JSONResponse(
            content=cleaned_data,
            media_type="application/json"
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
            media_type="application/json"
        )

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
    connected_clients.add(websocket)
    logger.info(f"Client connected. Total clients: {len(connected_clients)}")
    
    try:
        while True:
            stats = {
                "SMA": float(bot_state["indicators"]["SMA"][-1] if bot_state["indicators"]["SMA"] else 0.0),
                "RSI": float(bot_state["indicators"]["RSI"][-1] if bot_state["indicators"]["RSI"] else 0.0),
                "MACD": float(bot_state["indicators"]["MACD"][-1] if bot_state["indicators"]["MACD"] else 0.0)
            }
            
            await websocket.send_text(
                json.dumps({"stats": stats}, cls=TradingJSONEncoder)
            )
            
            await asyncio.sleep(1)
    except Exception as e:
        await websocket.send_text(
            json.dumps({"error": str(e)})
        )
        logger.error(f"WebSocket error: {e}")
    finally:
        connected_clients.remove(websocket)
        await websocket.close()
        logger.info(f"Client disconnected. Total clients: {len(connected_clients)}")

def start_api_server():
    uvicorn.run(
        app, 
        host="127.0.0.1",
        port=8001,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    start_api_server()