import requests
import logging
from trading.models import Trade

logger = logging.getLogger(__name__)

def execute_trade(user, symbol, trade_type, volume, take_profit=None):
    try:
        logger.info(f"Executing trade for user: {user.username}, API Key: {user.apikey}, MetaID: {user.metaid}")
        
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
            
            Trade.objects.create(
                user=user,
                symbol=symbol,
                trade_type=trade_type,
                volume=volume,
                price=result.get('price', 0),
                position_id=result.get('positionId')
            )
            
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
    

def close_trade(user, position_id):
    try:
        logger.info(f"Closing trade for user: {user.username}, API Key: {user.apikey}, MetaID: {user.metaid}")
        
        if not user.metaid:
            raise ValueError("MetaID is missing or invalid")
        
        position_url = f"https://mt-client-api-v1.london.agiliumtrade.ai/users/current/accounts/{user.metaid}/positions/{position_id}"
        headers = {
            "Accept": "application/json",
            "auth-token": user.apikey,
        }
        
        position_response = requests.get(position_url, headers=headers)
        
        if position_response.status_code == 200:
            position_data = position_response.json()
            profit = position_data.get('profit', 0)
            
            trade = Trade.objects.get(position_id=position_id)
            trade.price = profit
            trade.save()
        else:
            error_message = position_response.text
            logger.error(f"Error fetching position details: {error_message}")
            raise Exception(f"Error fetching position details: {error_message}")
        
        url = f"https://mt-client-api-v1.london.agiliumtrade.ai/users/current/accounts/{user.metaid}/trade"
        logger.debug(f"Trade URL: {url}")
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "auth-token": user.apikey,
        }
        
        payload = {
            "actionType": "POSITION_CLOSE_ID",
            "positionId": position_id,
        }
        
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Payload: {payload}")

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Trade closed successfully: {result}")
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
            logger.error(f"Error closing trade: {error_message}")
            raise Exception(f"Error closing trade: {error_message}")
    except Exception as e:
        logger.exception("Exception occurred while closing trade")
        raise e