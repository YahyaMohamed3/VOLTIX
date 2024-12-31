import yfinance as yf
from datetime import datetime, timedelta
import pytz
import pandas as pd

def format_large_number(value):
    """Formats a large number into M (millions) or T (trillions)."""
    if value is None:
        return None
    if value >= 1_000_000_000_000:  # Trillions
        return f"{value / 1_000_000_000_000:.2f}T"
    elif value >= 1_000_000:  # Millions
        return f"{value / 1_000_000:.2f}M"
    else:
        return f"{value:.2f}"

def fetch_stock_data(symbol):
    """
    Fetches live and fundamental stock data using Yahoo Finance, calculates turnover,
    and returns combined data.

    Args:
        symbol (str): Stock symbol to query.

    Returns:
        dict: Combined stock data including live data, fundamental data, market status, and calculated turnover.
    """
    try:
        # Fetch stock data using yfinance
        stock = yf.Ticker(symbol)

        # Define the current time and determine market status
        ny_time = datetime.now(pytz.timezone("America/New_York"))
        market_open = ny_time.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = ny_time.replace(hour=16, minute=0, second=0, microsecond=0)

        if ny_time < market_open:
            market_status = "Pre-Market"
        elif market_open <= ny_time <= market_close:
            market_status = "Live Market"
        else:
            market_status = "After Hours"

        # Fetch data based on market status
        if market_status == "After Hours":
            live_data = stock.history(period="1d", interval="1d")
        else:
            live_data = stock.history(period="1d", interval="1m")

        if live_data.empty:
            raise ValueError("No live data found for the given symbol.")

        # Extract the most recent data row
        latest_data = live_data.iloc[-1]
        current_close = latest_data["Close"]
        open_price = latest_data["Open"]
        high_price = latest_data["High"]
        low_price = latest_data["Low"]
        volume = latest_data["Volume"]

        # Fetch previous close from the stock info
        info = stock.info
        previous_close = info.get("previousClose", 0)

        # Calculate price change and percent change
        price_change = current_close - previous_close
        percent_change = price_change / previous_close * 100 if previous_close else 0

        # Organize live stock data
        live_stock_data = {
            "current_price": f"{current_close:.2f}",
            "previous_close": f"{previous_close:.2f}",
            "change": f"{price_change:.2f}",
            "change_percent": f"{percent_change:.2f}%",
            "open_price": f"{open_price:.2f}",
            "high_price": f"{high_price:.2f}",
            "low_price": f"{low_price:.2f}",
            "volume": format_large_number(volume),
        }

        # Fetch fundamental stock data
        fundamental_stock_data = {
            "market_cap": format_large_number(info.get("marketCap")),
            "pe_ratio": f"{info.get('trailingPE', 0):.2f}",
            "52_week_high": f"{info.get('fiftyTwoWeekHigh', 0):.2f}",
            "52_week_low": f"{info.get('fiftyTwoWeekLow', 0):.2f}",
        }

        # Calculate turnover
        average_price = (open_price + high_price + low_price + current_close) / 4
        turnover = average_price * volume if volume else 0

        # Combine all data
        combined_data = {
            "live_data": live_stock_data,
            "fundamental_data": fundamental_stock_data,
            "turnover": format_large_number(turnover),
            "market_status": market_status,
            "data_fetched_at": ny_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        }

        return combined_data

    except Exception as e:
        raise ValueError(f"Error fetching stock data: {e}")
    
