import yfinance as yf  # type: ignore
import pandas as pd
from datetime import datetime
from typing import Tuple, List, Dict, Any
from .strategies.momentum import Momentum
from .strategies.moving_average import MovingAverage
from .strategies.mean_reversion import MeanReversion
from .strategies.breakout import Breakout

def run_simulation(
    symbol: str,
    start_date: str,
    end_date: str,
    initial_capital: float,
    risk_tolerance: str,
    fee_percentage: float,
    strategy: str
) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    """
    Run a trading simulation with the specified strategy and parameters.
    
    Args:
        symbol: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        initial_capital: Starting capital for trading
        risk_tolerance: Risk profile ('High', 'Moderate', 'Low')
        fee_percentage: Trading fee as a decimal
        strategy: Trading strategy to use ('MAC', 'MT', 'MR', 'Breakout')
        
    Returns:
        Tuple of (trades list, performance metrics)
    """
    try:
        # Validate inputs
        if not isinstance(initial_capital, (int, float)) or initial_capital <= 0:
            raise ValueError("Initial capital must be a positive number")
        
        if risk_tolerance not in ['High', 'Moderate', 'Low']:
            raise ValueError("Risk tolerance must be 'High', 'Moderate', or 'Low'")
        
        if not isinstance(fee_percentage, float) or not 0 <= fee_percentage <= 1:
            raise ValueError("Fee percentage must be a float between 0 and 1")
        
        if strategy not in ["MAC", "MT", "MR", "Breakout"]:
            raise ValueError("Invalid strategy. Choose from: MAC, MT, MR, Breakout")
        
        # Calculate lookback period based on strategy
        lookback_days = {
            "MAC": 60,  # Increased to account for all indicators
            "MT": 21,
            "MR": 30,
            "Breakout": 55
        }[strategy]

        # Fetch and prepare data
        data = fetch_historical_data(symbol, start_date, end_date, lookback_days)
        
        if len(data) < lookback_days:
            raise ValueError(f"Insufficient data points. Need at least {lookback_days} days.")
        
        # Trim to requested period
        data = data[data.index >= pd.to_datetime(start_date)]
        
        # Execute strategy
        if strategy == "MAC":
            trades, performance = MovingAverage(
                data=data,
                initial_capital=initial_capital,
                risk_tolerance=risk_tolerance,  # Pass risk_tolerance directly
                fee_percentage=fee_percentage,
                ticker=symbol
            )
        elif strategy == "MT":
            trades, performance = Momentum(data, initial_capital, risk_tolerance, fee_percentage)
        elif strategy == "MR":
            trades, performance = MeanReversion(data, initial_capital, risk_tolerance, fee_percentage)
        else:  # Breakout
            trades, performance = Breakout(data, initial_capital, risk_tolerance, fee_percentage)

        if not trades and not performance:
            print(f"Warning: No trades executed for {symbol} from {start_date} to {end_date}")
        
        return trades, performance
        
    except Exception as e:
        print(f"Error running simulation: {str(e)}")
        raise

def fetch_historical_data(
    symbol: str,
    start_date: str,
    end_date: str,
    lookback_days: int = 0
) -> pd.DataFrame:
    """
    Fetch historical price data from Yahoo Finance.
    
    Args:
        symbol: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        lookback_days: Additional days of history needed for calculations
        
    Returns:
        DataFrame with price data
    """
    try:
        # Adjust start date for lookback period
        adjusted_start = pd.to_datetime(start_date) - pd.DateOffset(days=lookback_days)
        
        # Fetch data
        data = yf.download(
            symbol,
            start=adjusted_start.strftime("%Y-%m-%d"),
            end=end_date,
            progress=False
        )
        
        if data.empty:
            raise ValueError(f"No data found for symbol {symbol}")
        
        # Standardize column names
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]
        data.columns = [col.strip().title() for col in data.columns]
        
        # Clean up time zones and ensure proper datetime index
        data = data.tz_localize(None)
        data.index = pd.to_datetime(data.index)
        
        return data.sort_index(ascending=True)
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        raise