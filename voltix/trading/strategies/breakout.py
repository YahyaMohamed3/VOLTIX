import pandas as pd
import numpy as np
from ..utils import calculate_performance_metrics

def Breakout(data, initial_capital, risk_tolerance, fee_percentage):
    """
    Advanced breakout trading strategy with volatility-adjusted position sizing.
    
    Args:
        data (pd.DataFrame): Historical price data with OHLCV columns
        initial_capital (float): Starting capital for trading
        risk_tolerance (str): Risk tolerance level ('High', 'Moderate', 'Low')
        fee_percentage (float): Trading fee as a percentage
    """
    capital = float(initial_capital)
    position = 0.0
    entry_price = 0.0
    
    risk_profiles = {
        'High': {
            'allocation': 0.8,
            'lookback': 20,
            'atr_multiplier': 3,
            'profit_target': 2.5
        },
        'Moderate': {
            'allocation': 0.5,
            'lookback': 30,
            'atr_multiplier': 2.5,
            'profit_target': 2.0
        },
        'Low': {
            'allocation': 0.3,
            'lookback': 40,
            'atr_multiplier': 2,
            'profit_target': 1.5
        }
    }
    
    if risk_tolerance not in risk_profiles:
        raise ValueError("Invalid risk tolerance level")
        
    # Calculate indicators
    data['high_channel'] = data['High'].rolling(window=20).max()
    data['low_channel'] = data['Low'].rolling(window=20).min()
    
    # ATR calculation
    data['tr'] = np.maximum(
        data['High'] - data['Low'],
        np.maximum(
            abs(data['High'] - data['Close'].shift(1)),
            abs(data['Low'] - data['Close'].shift(1))
        )
    )
    data['atr'] = data['tr'].rolling(window=14).mean()
    
    # Volume indicators
    data['volume_ma'] = data['Volume'].rolling(window=20).mean()
    data['volume_std'] = data['Volume'].rolling(window=20).std()
    
    trades = []
    
    for i in range(40, len(data)):
        config = risk_profiles[risk_tolerance]
        
        close = float(data['Close'].iloc[i])
        high_channel = float(data['high_channel'].iloc[i])
        low_channel = float(data['low_channel'].iloc[i])
        atr = float(data['atr'].iloc[i])
        volume = float(data['Volume'].iloc[i])
        volume_ma = float(data['volume_ma'].iloc[i])
        
        # Volume surge detection
        volume_surge = volume > (volume_ma + 2 * data['volume_std'].iloc[i])
        
        # Buy condition: Breakout above channel with volume confirmation
        buy_condition = (
            position == 0 and
            close > high_channel and
            volume_surge
        )
        
        # Sell condition: Price breaks below channel or hits stop/target
        sell_condition = (
            position > 0 and
            (close < low_channel or
             close <= entry_price - config['atr_multiplier'] * atr or
             close >= entry_price + config['profit_target'] * config['atr_multiplier'] * atr)
        )
        
        if buy_condition:
            # Position sizing based on ATR
            risk_per_share = config['atr_multiplier'] * atr
            position_size = (capital * config['allocation']) / close
            position_size = min(position_size, capital / close)  # Ensure we don't exceed capital
            
            entry_cost = position_size * close
            fee = entry_cost * fee_percentage
            capital -= (entry_cost + fee)
            position = position_size
            entry_price = close
            
            trades.append({
                "action": "BUY",
                "date": data.index[i],
                "price": close,
                "position": position,
                "capital_left": capital,
                "reasons": {
                    "breakout": "Price broke above channel",
                    "volume_surge": volume_surge,
                    "atr": atr
                }
            })
            
        elif sell_condition:
            exit_value = position * close
            fee = exit_value * fee_percentage
            capital += (exit_value - fee)
            profit_loss = ((close - entry_price) / entry_price) * 100
            
            trades.append({
                "action": "SELL",
                "date": data.index[i],
                "price": close,
                "entry_price": entry_price,
                "exit_price": close,
                "profit_loss_percentage": round(profit_loss, 2),
                "capital_left": capital,
                "position": 0,
                "reasons": {
                    "channel_break": close < low_channel,
                    "stop_loss": close <= entry_price - config['atr_multiplier'] * atr,
                    "take_profit": close >= entry_price + config['profit_target'] * config['atr_multiplier'] * atr
                }
            })
            
            position = 0.0
            entry_price = 0.0
            
    return trades, calculate_performance_metrics(initial_capital, capital, trades)