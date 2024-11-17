from dataclasses import dataclass
from datetime import timedelta

@dataclass
class Config:
    TOKEN: str = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiIzNmNmNTVjZDQyZDEyZTIyMDdiMWUxMmZkZTY5NjM5YiIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJjb3B5ZmFjdG9yeS1hcGkiLCJtZXRob2RzIjpbImNvcHlmYWN0b3J5LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjM2Y2Y1NWNkNDJkMTJlMjIwN2IxZTEyZmRlNjk2MzliIiwiaWF0IjoxNzMxODU2NzI2LCJleHAiOjE3Mzk2MzI3MjZ9.my30hkFiDOQ-ywD5sXs0srCTK50qnJWhSbReGqKwBZVNtpw0Zhr6iahIXGvAmZKfjYiED-JoEG3TArm3G-dd6wOVvjDTEtPVJuq-k4AGNGib6kCwlbO9Nq8XMlDccdNj57JUCekINYV-TmxmGAyeiOxNqf9AipuDYjO49b6C-V3SAd-Gp_MgBQ9kU9Dis3i9BTwfhYocMaM8rWwBV8aVggXiBmlgTRqXm_5l0kZYF-IRq007fwtHU6wwa1vbIEzDFzXVUad31b4hkWX_fz_Tc5M_TULXxz-CEl4Rpgky2V699knFLuvjb6UN6ZhTr9T93UnILDg2ml90Bdn5W76fS4F-qYScfC6b0PHpL4-TdzGsT82q6D9whfBuJkp5OpDtHyTdcAl9g8Yed_zr7rkwPRR10XcSNUEwnpxaAhlt0n-ngNEI6GSTyipONGUVDKzpnVAZaTqQh3qFye_F1yzm4miNdnJDyI9pRSQTn7Vne2vUj1hVzJxH7SRDtUjsZZ9RM3oT7QIVEZ7qXeoCVyRPI2IX_EPQ3KqghlD43lYWbrUO6oL0cGXwGoejZg1Yy_nW5WyBhkBEXlZEdGd7MVQi57advPzWVs55IJCPR1ocMC3xxdHEOZaNr68kb94Z9Y84lrQf-cLDFEdWFPV0N7X6MbQio4GEYszp56DB-NKM9Qk"
    ACCOUNT_ID: str = "f5dfd441-10a8-4eeb-84b7-35fd0bacd2c2"
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