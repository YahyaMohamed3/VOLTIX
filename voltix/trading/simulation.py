import yfinance as yf # type: ignore
import pandas as pd
import numpy as np
from strategies.momentum import Momentum 
from strategies.moving_average import MovingAverage 
from strategies.mean_reversion import MeanReversion 
from strategies.breakout import Breakout 


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
    return trades, performance




def fetch_historical_data(symbol, start_date, end_date):
    """Fetch historical price data using yfinance."""
    data = yf.download(symbol, start=start_date, end=end_date)
    data['Date'] = data.index
    return data


symbol = "AAPL"  # Apple Inc. stock
start_date = "2024-01-01"
end_date = "2024-12-31"
initial_capital = 1000000  # Starting with $10,000
risk_tolerance = "High"  # Choose between "High", "Moderate", or "Low"
fee_percentage = 0.001  # 0.1% fee per trade
strategy = "MAC"  # Moving Average Crossover strategy

trades, performance = run_simulation(
    symbol, start_date, end_date, initial_capital, risk_tolerance, fee_percentage, strategy
)
    
# Output results
print("Trades executed:")
print(trades)
print("\nPerformance metrics:")
print(performance)
