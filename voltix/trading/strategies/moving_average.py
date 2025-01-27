import pandas as pd 
import numpy as np
from utils import calculate_performance_metrics


def MovingAverage(data, initial_capital, risk_tolerance, fee_percentage):
    """Advanced trading strategy with enhanced risk management."""
    capital = float(initial_capital)
    position = 0.0
    # Risk allocation with more nuanced parameters
    risk_profiles = {
        'High': {'allocation': 0.9, 'stop_loss': 0.05, 'take_profit': 0.15},
        'Moderate': {'allocation': 0.5, 'stop_loss': 0.03, 'take_profit': 0.10},
        'Low': {'allocation': 0.3, 'stop_loss': 0.02, 'take_profit': 0.07}
    }

    if risk_tolerance not in risk_profiles:
        raise ValueError("Invalid risk tolerance level")

    # Advanced technical indicators
    data['short_ma'] = data['Close'].rolling(window=5).mean()
    data['long_ma'] = data['Close'].rolling(window=20).mean()
    data['atr'] = data['Close'].diff().abs().rolling(window=14).mean()
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['rsi'] = 100 - (100 / (1 + rs))

    trades = []
    peak_price = 0
    entry_price = 0

    for i in range(1, len(data)):
        if pd.isna(data['short_ma'].iloc[i]) or pd.isna(data['long_ma'].iloc[i]):
            continue

        # Scalar values
        close_price = float(data['Close'].iloc[i])
        short_ma = float(data['short_ma'].iloc[i])
        long_ma = float(data['long_ma'].iloc[i])
        rsi = float(data['rsi'].iloc[i])

        risk_config = risk_profiles[risk_tolerance]

        # Advanced buy conditions with multiple filters
        buy_condition = (
            short_ma > long_ma and  # Trend confirmation
            rsi < 50 and  # Avoid overbought conditions
            position == 0  # No existing position
        )

        # Sell conditions with stop-loss and take-profit
        sell_condition = (
            short_ma < long_ma or  # Trend reversal
            (position > 0 and entry_price > 0 and (
                # Stop-loss triggered
                close_price <= entry_price * (1 - risk_config['stop_loss']) or
                # Take-profit triggered
                close_price >= entry_price * (1 + risk_config['take_profit'])
            ))
        )

        # Buy logic with dynamic position sizing
        if buy_condition:
            max_position_value = capital * risk_config['allocation']
            position_size = max_position_value / close_price
            
            capital -= max_position_value
            fee = max_position_value * fee_percentage
            capital -= fee
            position = position_size
            entry_price = close_price
            peak_price = close_price
            
            trades.append({
                "action": "BUY",
                "date": data['Date'].iloc[i],
                "price": close_price,
                "entry_price": close_price,
                "capital_left": capital,
                "position": position,
                "reasons": {
                    "short_ma": short_ma,
                    "long_ma": long_ma,
                    "rsi": rsi,
                    "trend": "Short MA crossed above Long MA",
                    "rsi_condition": "RSI below 50 indicating potential upside"
                }
            })
            
        elif sell_condition and position > 0:
            sell_value = position * close_price
            capital += sell_value
            fee = sell_value * fee_percentage
            capital -= fee
            profit_loss = ((close_price - entry_price) / entry_price) * 100
            
            trades.append({
                "action": "SELL",
                "date": data['Date'].iloc[i],
                "price": close_price,
                "entry_price": entry_price,
                "exit_price": close_price,
                "profit_loss_percentage": round(profit_loss, 2),
                "capital_left": capital,
                "position": 0,
                "reasons": {
                    "short_ma": short_ma,
                    "long_ma": long_ma,
                    "rsi": rsi,
                    "trend": "Short MA crossed below Long MA" if short_ma < long_ma else None,
                    "stop_loss": close_price <= entry_price * (1 - risk_config['stop_loss']),
                    "take_profit": close_price >= entry_price * (1 + risk_config['take_profit'])
                }
            })
            
            position = 0.0
            entry_price = 0
            peak_price = 0

    return trades, calculate_performance_metrics(initial_capital, capital, trades)