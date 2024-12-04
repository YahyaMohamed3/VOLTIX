import os
import requests
from datetime import datetime
from django.conf import settings
from .models import Market
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

def fetch_and_store(symbol, interval="1min"):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        logger.error("API key is missing! Please set it in your environment variables.")
        return

    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={api_key}&outputsize=full"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error if the request was unsuccessful
        data = response.json().get(f"Time Series ({interval})", {})
        
        if not data:
            logger.warning(f"No data returned for {symbol}. Check the symbol or try again later.")
            return

        # Prepare data for bulk insert
        market_data = []
        for timestamp, values in data.items():
            market_data.append(
                Market(
                    symbol=symbol,
                    timestamp=datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
                    open=float(values["1. open"]),
                    high=float(values["2. high"]),
                    low=float(values["3. low"]),
                    close=float(values["4. close"]),
                    volume=int(values["5. volume"])
                )
            )
        
        # Bulk insert the data for efficiency
        if market_data:
            Market.objects.bulk_create(market_data)
            logger.info(f"Historical data for {symbol} stored successfully.")
        else:
            logger.warning(f"No valid data to store for {symbol}.")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}")

def fetch_live_price(symbol):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        logger.error("API key is missing! Please set it in your environment variables.")
        return

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("Global Quote", {})

        if data:
            price = float(data["05. price"])
            volume = int(data["06. volume"])
            timestamp = datetime.now()  # Use current timestamp for live data

            # Update or create the latest price in the Market model
            Market.objects.update_or_create(
                symbol=symbol,
                timestamp=timestamp,
                defaults={
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": volume
                }
            )
            logger.info(f"Live data for {symbol} updated successfully.")
        else:
            logger.warning(f"No live data returned for {symbol}.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching live data for {symbol}: {e}")
