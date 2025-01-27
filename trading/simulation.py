import yfinance as yf # type: ignore
import pandas as pd
import numpy as np
from .strategies.momentum import Momentum 
from .strategies.moving_average import MovingAverage 
from .strategies.mean_reversion import MeanReversion 
from .strategies.breakout import Breakout 


def run_simulation(symbol, start_date, end_date, initial_capital, risk_tolerance, fee_percentage , strategy):
    data = fetch_historical_data(symbol, start_date, end_date)
    if strategy == "MAC":
        trades, performance = MovingAverage(data, initial_capital, risk_tolerance, fee_percentage)
    elif strategy == "MT":
        trades, performance = Momentum(data, initial_capital, risk_tolerance, fee_percentage)
    elif strategy == "MR":
        trades, performance = MeanReversion(data, initial_capital, risk_tolerance, fee_percentage)
    else:
        trades, performance = Breakout(data, initial_capital, risk_tolerance, fee_percentage)
    print(trades)
    print(performance)
    return trades, performance




def fetch_historical_data(symbol, start_date, end_date):
    """Fetch historical price data using yfinance."""
    data = yf.download(symbol, start=start_date, end=end_date)
    data['Date'] = data.index
    return data

