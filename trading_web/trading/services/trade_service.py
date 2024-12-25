import requests
import logging

logger = logging.getLogger(__name__)

def execute_trade(user, symbol, trade_type, volume, take_profit=None):
    try:
        logger.info(f"Executing trade for user: {user.username}, API Key: {user.apikey}, MetaID: {user.metaid}")
        
        # Verify metaid
        if not user.metaid:
            raise ValueError("MetaID is missing or invalid")
        
        url = f"https://mt-client-api-v1.london.agiliumtrade.ai/users/current/accounts/{user.metaid}/trade"
        logger.debug(f"Trade URL: {url}")
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "auth-token": user.apikey,
        }
        
        payload = {
            "actionType": trade_type,
            "symbol": symbol,
            "volume": volume,
        }
        
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Payload: {payload}")

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Trade executed successfully: {result}")
            return result
        elif response.status_code == 401:
            error_message = response.text
            logger.error(f"UnauthorizedError: {error_message}")
            logger.error(f"API Key: {user.apikey}")
            raise Exception(f"UnauthorizedError: {error_message}")
        elif response.status_code == 404:
            error_message = response.text
            logger.error(f"NotFoundError: {error_message}")
            raise Exception(f"NotFoundError: {error_message}")
        else:
            error_message = response.text
            logger.error(f"Error executing trade: {error_message}")
            raise Exception(f"Error executing trade: {error_message}")
    except Exception as e:
        logger.exception("Exception occurred while executing trade")
        raise e