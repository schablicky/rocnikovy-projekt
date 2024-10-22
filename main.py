import os
import asyncio
import numpy as np
import pandas as pd
import tensorflow as tf
from metaapi_cloud_sdk import MetaApi
from datetime import datetime
import matplotlib.pyplot as plt

# definovani metaapi token, login, heslo, server a symbol
TOKEN = os.getenv('TOKEN') or 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiIzNmNmNTVjZDQyZDEyZTIyMDdiMWUxMmZkZTY5NjM5YiIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJjb3B5ZmFjdG9yeS1hcGkiLCJtZXRob2RzIjpbImNvcHlmYWN0b3J5LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjM2Y2Y1NWNkNDJkMTJlMjIwN2IxZTEyZmRlNjk2MzliIiwiaWF0IjoxNzI5MzM4MTc1fQ.DRMzjiwpi9f1vF2gMco72K3y6j4Qs7JgEaFGjCAbGyKajPE0p6oyxoZDUHNfWtUtG0n5AToQORPKjfMsMMQOU43MvJ4-VTl_q2ty-ZVquu-iDrSFUHH-sohkZnSNfZmlu1_Cn8jH3j3kDYW7n7HF9ls2rhEO5iMfvO2Wlfw06BF4CkaVES8F9ydbiNTq1O9NrnpOmklQ10DDy08BuOiR5a4kQ63rEk853kBI83zhV7Tofzr5IbAMUV-3h1uJ4ysf7KZ3B9dypDDv592uqFupipwqgVfmmWOha2cJTwK1doJasc37FKu3hO5DMWu67Zn2hc2AG61qv1kEa_3FEQ6UwISvUOVI6t0JEbLIYyxwXgORxnqmPwjpTpUcgAdjzogpt2STtylpeYt9BksE8jGHvziATc_BErbd5hg2rd4DZCkxdQ5aVJ6qjM2wRAiXup2NyAn8Pr0sKkCM6v7g3hTkU9KzCI7hBSBHcENGBJDFUYNexSgloSkTgMCIiC_WhEXvH-Uh5KfflJ5IcC67gIMw696rIq8Xe7g1IvToN5n3hLIz4hponGsnl9sTbrS93mQClP02hL8kOjR5Zgmhj3WozRQBvqscECtaXOnuRWqn7fw92ttTZJj6lKfv8FEDWfWZNT_qoS_rpAsVq1cLwp2ezypAKyVg_g52Lgm5IlcUEbQ'
LOGIN = os.getenv('LOGIN') or '156801675'  # MT login
PASSWORD = os.getenv('PASSWORD') or 'igv2xha'  # MT heslo
SERVER = os.getenv('SERVER') or 'MetaQuotes-Demo'
SYMBOL = 'EURUSD'


async def main():
    # MetaAPI client
    meta_api = MetaApi(TOKEN)
    # definovani historickych dat
    end_time = datetime.now()
    start_time = end_time - pd.Timedelta(days=7)

  
    data = await fetch_historical_data(meta_api, SYMBOL, start_time, end_time)
    if data is None:
        print("Failed to fetch data")
        return

    # pripraveni dat na trenovani
    data['time'] = pd.to_datetime(data['time'])
    data.set_index('time', inplace=True)
    data['volume'] = pd.to_numeric(data['volume'])
    data['price'] = pd.to_numeric(data['price'])

    # vytvoreni a trenovani tensorflow agenta
    agent = TensorFlowAgent((data.shape[1], 1))
    data_to_train = data[['volume', 'price']].values.reshape(-1, data.shape[1], 1)
    agent.fit(data_to_train, data['price'].values, epochs=15)

  
    predictions = agent.predict(data_to_train)
    print(predictions)

    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 6))
    plt.plot(data['price'].values, label='Actual')
    plt.plot(predictions, label='Predicted')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('Predictions vs Actual')
    plt.legend()
    plt.show()


async def fetch_historical_data(meta_api, symbol, start_time, end_time):
    try:
        # pridani testovaciho meta account
        accounts = await meta_api.metatrader_account_api.get_accounts_with_infinite_scroll_pagination()
        account = None
        for item in accounts:
            if item.login == LOGIN and item.type.startswith('cloud'):
                account = item
                break
        if not account:
            print('Adding MT4 account to MetaApi')
            account = await meta_api.metatrader_account_api.create_account(
                {
                    'name': 'Test account',
                    'type': 'cloud',
                    'login': LOGIN,
                    'password': PASSWORD,
                    'erver': SERVER,
                    'platform': 't4',
                    'agic': 1000,
                }
            )
        else:
            print('MT4 account already added to MetaApi')

        # cekani na pripojeni k brokerovi
        print('Deploying account')
        await account.deploy()
        print('Waiting for API server to connect to broker (may take couple of minutes)')
        await account.wait_connected()

        # Connect to MetaApi API
        connection = account.get_streaming_connection()
        await connection.connect()

        # Wait until terminal state synchronized to the local state
        print('Waiting for SDK to synchronize to terminal state (may take some time depending on your history size)')
        await connection.wait_synchronized()

        # Access local copy of terminal state
        print('Testing terminal state access')
        terminal_state = connection.terminal_state

        # Fetch historical deals for the specified symbol and time range
        history_storage = connection.history_storage
        deals = history_storage.get_deals_by_time_range(start_time, end_time)

        if deals:
            try:
                data = pd.DataFrame([
                    {
                        'time': deal.get('time', None),
                        'type': deal.get('type', None),
                        'volume': deal.get('volume', None),
                        'price': deal.get('price', None)
                    } for deal in deals
                ])
            except Exception as e:
                print(f"Chyba při zpracování dat: {str(e)}")
                return None
        else:
            print("Žádné obchody nalezeny.")
            return pd.DataFrame()

        return data
    except Exception as err:
        print(meta_api.format_error(err))
        return None


class TensorFlowAgent:
    def __init__(self, input_shape):
        self.model = self._build_model(input_shape)

    def _build_model(self, input_shape):
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(75, return_sequences=True, input_shape=input_shape),
            tf.keras.layers.LSTM(50),
            tf.keras.layers.Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    def fit(self, data, target, epochs):
        self.model.fit(data, target, epochs=epochs)

    def predict(self, data):
        return self.model.predict(data)


asyncio.run(main())
