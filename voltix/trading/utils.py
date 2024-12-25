import yfinance as yf
def fetch_stock_data(symbol):
    """
    Fetches live and fundamental stock data using yfinance and calculates turnover.
    
    Args:
        symbol (str): Stock symbol to query.

    Returns:
        dict: Combined stock data including live data, fundamental data, and calculated turnover.
    """
    try:
        # Fetch stock data using yfinance
        stock = yf.Ticker(symbol)
        history = stock.history(period="5d")  # Fetch data for the last 5 days
        if history.empty:
            raise ValueError("No data found for the given symbol and period.")

        # Ensure we have at least two data points for current and previous close
        if len(history) < 2:
            raise ValueError("Insufficient data to calculate previous close and changes.")

        current_close = history["Close"].iloc[-1]  # Current day's close
        previous_close = history["Close"].iloc[-2]  # Previous day's close

        # Calculate change and change percent
        change = current_close - previous_close
        change_percent = (change / previous_close) * 100

        live_stock_data = {
            "price": current_close,
            "previous_close": previous_close,
            "change": change,
            "change_percent": change_percent,
            "open": history["Open"].iloc[-1],
            "high": history["High"].iloc[-1],
            "low": history["Low"].iloc[-1],
            "volume": history["Volume"].iloc[-1],
        }

        # Extract fundamental data
        info = stock.info
        fundamental_stock_data = {
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
        }

        # Calculate turnover
        average_price = (
            live_stock_data["open"]
            + live_stock_data["high"]
            + live_stock_data["low"]
            + live_stock_data["price"]
        ) / 4
        turnover = average_price * live_stock_data["volume"]

        # Combine all data
        combined_data = {
            "live_data": live_stock_data,
            "fundamental_data": fundamental_stock_data,
            "turnover": turnover,
        }

        return combined_data

    except Exception as e:
        raise ValueError(f"Error fetching stock data: {e}")