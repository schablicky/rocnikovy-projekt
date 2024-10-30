import os
import asyncio
import metaapi_cloud_sdk
import pandas as pd
import tensorflow as tf
from metaapi_cloud_sdk import MetaApi
from datetime import datetime




# Define your MetaAPI token, MT login, password, and server name
TOKEN = os.getenv('TOKEN')
LOGIN = os.getenv('LOGIN')   # MT login
PASSWORD = os.getenv('PASSWORD')  # MT heslo
SERVER = os.getenv('SERVER') 
SYMBOL = 'EURUSD'


async def main():
    # Initialize MetaAPI client
    meta_api = MetaApi(TOKEN)
    # Define time range for historical data
    end_time = datetime.now()
    start_time = end_time - pd.Timedelta(days=7)

    # Fetch historical data
    data = await fetch_historical_data(meta_api, SYMBOL, start_time, end_time)
    if data is None:
        print("Failed to fetch data")
        return

    # Prepare data for training
    data['time'] = pd.to_datetime(data['time'])
    data.set_index('time', inplace=True)
    data['volume'] = pd.to_numeric(data['volume'])
    data['price'] = pd.to_numeric(data['price'])

    # Create and train TensorFlow model
    agent = TensorFlowAgent((data.shape[1], 1))
    data_to_train = data[['volume', 'price']].values.reshape(-1, data.shape[1], 1)
    agent.fit(data_to_train, data['price'].values, epochs=15)

    # Use the trained model for predictions
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
            accounts = await meta_api.metatrader_account_api.get_accounts_with_infinite_scroll_pagination()
        except metaapi_cloud_sdk.clients.method_access_exception.MethodAccessException as e:
            print(f"Chyba přístupu k metodě: {str(e)}")
            return None  # nebo raise e
        except Exception as err:
            print(meta_api.format_error(err))
            return None
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
                    'server': SERVER,
                    'platform': 't4',
                    'agic': 1000,
                }
            )
        else:
            print('MT4 account already added to MetaApi')

        # Wait until account is deployed and connected to broker
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
