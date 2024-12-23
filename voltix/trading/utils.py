import requests

def fetch_stock_data(symbol):
    """
    Fetches live and fundamental stock data from Alpha Vantage and calculates turnover.
    
    Args:
        api_key (str): Alpha Vantage API key.
        symbol (str): Stock symbol to query.

    Returns:
        dict: Combined stock data including live data, fundamental data, and calculated turnover.
    """
    api_key = "X1YKLOCYNSVW5A9R"
    try:
        # Fetch live stock data
        live_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
        live_response = requests.get(live_url)
        live_data = live_response.json()
        print(symbol)

        if "Global Quote" not in live_data:
            raise ValueError("Unable to fetch live data. Check your API key or symbol.")

        live_quote = live_data.get("Global Quote", {})
        live_stock_data = {
            "price": live_quote.get("05. price"),
            "change": live_quote.get("09. change"),
            "change_percent": live_quote.get("10. change percent"),
            "volume": live_quote.get("06. volume"),
            "previous_close": live_quote.get("08. previous close"),
            "open": live_quote.get("02. open"),
            "high": live_quote.get("03. high"),
            "low": live_quote.get("04. low"),
        }

        # Fetch fundamental stock data
        fundamental_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
        fundamental_response = requests.get(fundamental_url)
        fundamental_data = fundamental_response.json()

        if not fundamental_data:
            raise ValueError("Unable to fetch fundamental data. Check your API key or symbol.")

        fundamental_stock_data = {
            "market_cap": fundamental_data.get("MarketCapitalization"),
            "pe_ratio": fundamental_data.get("PERatio"),
            "52_week_high": fundamental_data.get("52WeekHigh"),
            "52_week_low": fundamental_data.get("52WeekLow"),
        }

        # Calculate turnover
        try:
            open_price = float(live_stock_data["open"])
            high_price = float(live_stock_data["high"])
            low_price = float(live_stock_data["low"])
            close_price = float(live_stock_data["price"])
            volume = int(live_stock_data["volume"])

            average_price = (open_price + high_price + low_price + close_price) / 4
            turnover = average_price * volume
        except (ValueError, TypeError) as e:
            raise ValueError(f"Error calculating turnover: {e}")

        # Combine all data
        combined_data = {
            "live_data": live_stock_data,
            "fundamental_data": fundamental_stock_data,
            "turnover": turnover,
        }

        return combined_data

    except requests.RequestException as e:
        raise ValueError(f"Request error: {e}")
    except ValueError as e:
        raise ValueError(e)
