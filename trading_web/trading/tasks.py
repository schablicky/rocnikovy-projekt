from celery import shared_task
from .services.market_data_service import fetch_and_save_market_data

@shared_task
def fetch_and_save_market_data_task():
    fetch_and_save_market_data()