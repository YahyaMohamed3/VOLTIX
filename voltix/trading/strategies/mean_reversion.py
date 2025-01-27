import pandas as pd
import numpy as np
from ..utils import calculate_performance_metrics

def MeanReversion(data, initial_capital, risk_tolerance, fee_percentage):
    """
    Advanced mean reversion strategy using Bollinger Bands and RSI with dynamic position sizing.
    
    Args:
        data (pd.DataFrame): Historical price data with OHLCV columns
        initial_capital (float): Starting capital for trading
        risk_tolerance (str): Risk tolerance level ('High', 'Moderate', 'Low')
        fee_percentage (float): Trading fee as percentage
    """
    capital = float(initial_capital)
    position = 0.0
    entry_price = 0.0
    
    risk_profiles = {
        'High': {
            'allocation': 0.8,
            'bb_std': 2.5,
            'rsi_low': 25,
            'rsi_high': 75,
            'stop_loss': 0.05,
            'take_profit': 0.08
        },
        'Moderate': {
            'allocation': 0.5,
            'bb_std': 2.0,
            'rsi_low': 30,
            'rsi_high': 70,
            'stop_loss': 0.04,
            'take_profit': 0.06
        },
        'Low': {
            'allocation': 0.3,
            'bb_std': 1.5,
            'rsi_low': 35,
            'rsi_high': 65,
            'stop_loss': 0.03,
            'take_profit': 0.04
        }
    }
    
    if risk_tolerance not in risk_profiles:
        raise ValueError("Invalid risk tolerance level")
    
    # Calculate Bollinger Bands
    data['sma'] = data['Close'].rolling(window=20).mean()
    data['std'] = data['Close'].rolling(window=20).std()
    
    # RSI calculation
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['rsi'] = 100 - (100 / (1 + rs))
    
    # Historical volatility
    data['volatility'] = data['Close'].pct_change().rolling(window=20).std()
    
    trades = []
    
    for i in range(20, len(data)):
        config = risk_profiles[risk_tolerance]
        
        close = float(data['Close'].iloc[i])
        sma = float(data['sma'].iloc[i])
        std = float(data['std'].iloc[i])
        rsi = float(data['rsi'].iloc[i])
        volatility = float(data['volatility'].iloc[i])
        
        upper_band = sma + config['bb_std'] * std
        lower_band = sma - config['bb_std'] * std
        
        # Buy when oversold and below lower band
        buy_condition = (
            position == 0 and
            close < lower_band and
            rsi < config['rsi_low']
        )
        
        # Sell when overbought and above upper band
        sell_condition = (
            position > 0 and
            (close > upper_band or
             rsi > config['rsi_high'] or
             close <= entry_price * (1 - config['stop_loss']) or
             close >= entry_price * (1 + config['take_profit']))
        )
        
        if buy_condition:
            # Adjust position size based on volatility
            volatility_factor = 1 - (volatility * 10)
            volatility_factor = max(0.3, min(1, volatility_factor))
            
            position_value = capital * config['allocation'] * volatility_factor
            position_size = position_value / close
            
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
                    "bollinger": "Below lower band",
                    "rsi": f"Oversold at {round(rsi, 2)}",
                    "volatility_factor": round(volatility_factor, 2)
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
                    "bollinger": "Above upper band" if close > upper_band else None,
                    "rsi": f"Overbought at {round(rsi, 2)}" if rsi > config['rsi_high'] else None,
                    "stop_loss": close <= entry_price * (1 - config['stop_loss']),
                    "take_profit": close >= entry_price * (1 + config['take_profit'])
                }
            })
            
            position = 0.0
            entry_price = 0.0
            
    return trades, calculate_performance_metrics(initial_capital, capital, trades)