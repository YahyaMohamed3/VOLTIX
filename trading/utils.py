import yfinance as yf # type: ignore
from datetime import datetime, timedelta
import pytz
import pandas as pd
import numpy as np

def format_large_number(value):
    """Formats a large number into M (millions) or T (trillions)."""
    if value is None:
        return None
    if value >= 1_000_000_000_000:  # Trillions
        return f"{value / 1_000_000_000_000:.2f}T"
    elif value >= 1_000_000_000:  # Billions   
        return f"{value / 1_000_000_000:.2f}B"
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

def calculate_performance_metrics(initial_capital, final_capital, trades):
    """Calculate comprehensive trading performance metrics."""
    # Basic metrics
    total_return = (final_capital - initial_capital) / initial_capital * 100
    total_trades = len(trades)
    buy_trades = sum(1 for trade in trades if trade['action'] == 'BUY')
    sell_trades = sum(1 for trade in trades if trade['action'] == 'SELL')
    
    # Profit per trade
    trade_profits = []
    current_position = 0
    entry_price = 0
    for trade in trades:
        if trade['action'] == 'BUY':
            current_position = trade['position']
            entry_price = trade['price']
        elif trade['action'] == 'SELL':
            trade_profit = (trade['price'] - entry_price) / entry_price * 100
            trade_profits.append(trade_profit)
            current_position = 0
    
    # Advanced metrics
    avg_trade_profit = np.mean(trade_profits) if trade_profits else 0
    win_rate = sum(1 for profit in trade_profits if profit > 0) / len(trade_profits) * 100 if trade_profits else 0
    max_drawdown = min(trade_profits) if trade_profits else 0
    
    return {
        'total_return_percentage': round(total_return, 2),
        'final_capital': round(final_capital, 2),
        'total_trades': total_trades,
        'buy_trades': buy_trades,
        'sell_trades': sell_trades,
        'average_trade_profit_percentage': round(avg_trade_profit, 2),
        'win_rate_percentage': round(win_rate, 2),
        'max_drawdown_percentage': round(max_drawdown, 2)
    }



