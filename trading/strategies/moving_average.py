import pandas as pd
import numpy as np
from ..utils import calculate_performance_metrics

def MovingAverage(data, initial_capital, risk_tolerance, fee_percentage):
    """
    Enhanced moving average crossover strategy with improved risk management and trend confirmation.
    
    Args:
        data (pd.DataFrame): Historical price data with multi-level columns from yfinance
        initial_capital (float): Starting capital for trading
        risk_tolerance (str): Risk tolerance level ('High', 'Moderate', 'Low')
        fee_percentage (float): Trading fee as percentage
    """
    capital = float(initial_capital)
    position = 0.0
    entry_price = 0.0
    monthly_trades = 0
    current_month = None
    
    risk_profiles = {
        'High': {
            'allocation': 0.8,
            'stop_loss': 0.05,
            'trailing_stop': 0.03,
            'max_monthly_trades': 4,
            'min_holding_days': 5
        },
        'Moderate': {
            'allocation': 0.5,
            'stop_loss': 0.04,
            'trailing_stop': 0.02,
            'max_monthly_trades': 3,
            'min_holding_days': 7
        },
        'Low': {
            'allocation': 0.3,
            'stop_loss': 0.03,
            'trailing_stop': 0.015,
            'max_monthly_trades': 2,
            'min_holding_days': 10
        }
    }

    if risk_tolerance not in risk_profiles:
        raise ValueError("Invalid risk tolerance level")

    # Create a working DataFrame with the correct price columns
    df = pd.DataFrame()
    df['Close'] = data['Close']['AAPL']
    df['High'] = data['High']['AAPL']
    df['Low'] = data['Low']['AAPL']
    df['Volume'] = data['Volume']['AAPL']
    
    # Enhanced technical indicators
    df['short_ma'] = df['Close'].rolling(window=10).mean()  # Faster MA for better responsiveness
    df['long_ma'] = df['Close'].rolling(window=30).mean()   # Longer MA for better trend confirmation
    
    # Calculate ATR
    df['tr'] = np.maximum(
        df['High'] - df['Low'],
        np.maximum(
            abs(df['High'] - df['Close'].shift(1)),
            abs(df['Low'] - df['Close'].shift(1))
        )
    )
    df['atr'] = df['tr'].rolling(window=14).mean()
    
    # Volume analysis
    df['volume_ma'] = df['Volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['Volume'] / df['volume_ma']
    
    trades = []
    highest_price = 0
    days_in_trade = 0
    
    for i in range(30, len(df)):
        config = risk_profiles[risk_tolerance]
        trade_date = df.index[i]
        
        # Reset monthly trade counter
        if current_month != trade_date.month:
            current_month = trade_date.month
            monthly_trades = 0
        
        close_price = float(df['Close'].iloc[i])
        short_ma = float(df['short_ma'].iloc[i])
        long_ma = float(df['long_ma'].iloc[i])
        volume_ratio = float(df['volume_ratio'].iloc[i])
        atr = float(df['atr'].iloc[i])
        
        # Update trailing stop if in position
        if position > 0 and close_price > highest_price:
            highest_price = close_price
        
        # Enhanced buy conditions
        buy_condition = (
            position == 0 and
            short_ma > long_ma and  # Basic MA crossover
            short_ma > df['short_ma'].iloc[i-1] and  # Rising short MA
            volume_ratio > 1.2 and  # Above average volume
            monthly_trades < config['max_monthly_trades']  # Monthly trade limit
        )

        # Enhanced sell conditions
        sell_condition = (
            position > 0 and
            (
                # Regular MA crossover exit
                (short_ma < long_ma and days_in_trade >= config['min_holding_days']) or
                # Stop loss
                close_price <= entry_price * (1 - config['stop_loss']) or
                # Trailing stop
                close_price <= highest_price * (1 - config['trailing_stop'])
            )
        )

        if buy_condition:
            # Position sizing with ATR-based risk
            risk_amount = capital * config['allocation']
            position_size = risk_amount / (close_price * (1 + config['stop_loss']))
            position_size = min(position_size, capital / close_price)
            
            entry_cost = position_size * close_price
            fee = entry_cost * fee_percentage
            capital -= (entry_cost + fee)
            position = position_size
            entry_price = close_price
            highest_price = close_price
            days_in_trade = 0
            monthly_trades += 1
            
            trades.append({
                "action": "BUY",
                "date": trade_date,
                "price": close_price,
                "entry_price": close_price,
                "capital_left": capital,
                "position": position,
                "reasons": {
                    "trend": "Short MA crossed above Long MA",
                    "momentum": f"Rising short MA: {round(short_ma - df['short_ma'].iloc[i-1], 2)}",
                    "volume": f"Above average: {round(volume_ratio, 2)}x",
                    "risk_amount": round(risk_amount, 2)
                }
            })
            
        elif sell_condition:
            exit_value = position * close_price
            fee = exit_value * fee_percentage
            capital += (exit_value - fee)
            profit_loss = ((close_price - entry_price) / entry_price) * 100
            
            trades.append({
                "action": "SELL",
                "date": trade_date,
                "price": close_price,
                "entry_price": entry_price,
                "exit_price": close_price,
                "profit_loss_percentage": round(profit_loss, 2),
                "capital_left": capital,
                "position": 0,
                "reasons": {
                    "trend": "Short MA crossed below Long MA" if short_ma < long_ma else None,
                    "stop_loss": close_price <= entry_price * (1 - config['stop_loss']),
                    "trailing_stop": close_price <= highest_price * (1 - config['trailing_stop']),
                    "days_held": days_in_trade
                }
            })
            
            position = 0.0
            entry_price = 0.0
            highest_price = 0
            days_in_trade = 0
            
        if position > 0:
            days_in_trade += 1

    return trades, calculate_performance_metrics(initial_capital, capital, trades)