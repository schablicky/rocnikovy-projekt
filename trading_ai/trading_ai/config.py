from dataclasses import dataclass
from datetime import timedelta

@dataclass
class Config:
    TOKEN: str = ""
    ACCOUNT_ID: str = ""
    SYMBOL: str = "EURUSD"
    TIMEFRAME: str = "1m"
    LOOKBACK_DAYS: int = 7
    INITIAL_BALANCE: float = 10000.0
    TRANSACTION_COST: float = 0.1
    BATCH_SIZE: int = 32
    BUFFER_SIZE: int = 10000
    TRAINING_EPISODES: int = 1000
    MAX_POSITION_SIZE: float = 0.2  # Max 20% of balance per trade
    MAX_DRAWDOWN: float = 0.1  # Max 10% drawdown
    HIGH_WATER_MARK_REWARD: float = 1.0  # Reward for new equity highs  
    DRAWDOWN_PENALTY: float = 2.0  # Penalty for exceeding max drawdown
    TRANSACTION_COST: float = 0.05  # Reduced transaction cost
