import aiohttp
import logging

logger = logging.getLogger(__name__)

async def execute_trade(user, symbol, trade_type, volume):
    try:
        logger.info(f"Executing trade for user: {user.username}, API Key: {user.apikey}, MetaID: {user.metaid}")
        
        # Verify metaid
        if not user.metaid:
            raise ValueError("MetaID is missing or invalid")
        
        url = f"https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts/{user.metaid}/trade"
        logger.debug(f"Trade URL: {url}")
        
        headers = {
            'auth-token': user.apikey,
            'Content-Type': 'application/json'
        }
        payload = {
            "symbol": symbol,
            "type": trade_type,
            "volume": volume
        }
        logger.debug(f"Payload: {payload}")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Trade executed successfully: {result}")
                    return result
                elif response.status == 404:
                    error_message = await response.text()
                    logger.error(f"NotFoundError: {error_message}")
                    raise Exception(f"NotFoundError: {error_message}")
                else:
                    error_message = await response.text()
                    logger.error(f"Error executing trade: {error_message}")
                    raise Exception(f"Error executing trade: {error_message}")
    except Exception as e:
        logger.exception("Exception occurred while executing trade")
        raise e