from celery import shared_task
from .utils import fetch_live_price  # Assuming fetch_live_price is defined in fetch_data.py
import logging

logger = logging.getLogger(__name__)

@shared_task
def fetch_live_price_task(symbols):
    """
    Celery task to fetch live price for multiple symbols.
    """
    for symbol in symbols:
        try:
            fetch_live_price(symbol)  # This should call your function that fetches live prices
        except Exception as e:
            logger.error(f"Error fetching live price for {symbol}: {e}")
