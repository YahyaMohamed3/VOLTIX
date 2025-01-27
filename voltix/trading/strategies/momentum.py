import pandas as pd
import numpy as np
from ..utils import calculate_performance_metrics

def Momentum(data, initial_capital, risk_tolerance, fee_percentage):
    """
    Enhanced momentum-based trading strategy with improved risk management and entry/exit conditions.
    
    Args:
        data (pd.DataFrame): Historical price data with OHLCV columns
        initial_capital (float): Starting capital for trading
        risk_tolerance (str): Risk tolerance level ('High', 'Moderate', 'Low')
        fee_percentage (float): Trading fee as a percentage
    
    Returns:
        tuple: (list of trades, performance metrics dictionary)
    """
    capital = float(initial_capital)
    position = 0.0
    entry_price = 0.0
    monthly_loss = 0.0
    current_month = None
    trailing_stop = 0.0

    # Enhanced risk profiles with trailing stops and partial profit taking
    risk_profiles = {
        'High': {
            'allocation': 0.8,
            'initial_stop': 0.05,
            'trailing_stop': 0.03,
            'take_profit_1': 0.1,
            'take_profit_2': 0.15,
            'max_monthly_loss': 0.15
        },
        'Moderate': {
            'allocation': 0.5,
            'initial_stop': 0.04,
            'trailing_stop': 0.02,
            'take_profit_1': 0.08,
            'take_profit_2': 0.12,
            'max_monthly_loss': 0.1
        },
        'Low': {
            'allocation': 0.3,
            'initial_stop': 0.03,
            'trailing_stop': 0.015,
            'take_profit_1': 0.06,
            'take_profit_2': 0.09,
            'max_monthly_loss': 0.07
        }
    }

    if risk_tolerance not in risk_profiles:
        raise ValueError("Invalid risk tolerance level")

    # Calculate momentum indicators
    data['roc'] = data['Close'].pct_change(periods=10) * 100
    data['roc_ma'] = data['roc'].rolling(window=3).mean()
    
    # Enhanced MFI calculation
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    money_flow = typical_price * data['Volume']
    positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
    negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)
    positive_mf = positive_flow.rolling(window=14).sum()
    negative_mf = negative_flow.rolling(window=14).sum()
    mfi_ratio = positive_mf / negative_mf
    data['mfi'] = 100 - (100 / (1 + mfi_ratio))

    # Enhanced RSI calculation
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['rsi'] = 100 - (100 / (1 + rs))

    # Volatility calculation for position sizing
    data['volatility'] = data['Close'].pct_change().rolling(window=20).std()

    trades = []
    peak_price = 0
    partial_position = False

    for i in range(20, len(data)):  # Start after all indicators have enough data
        close_price = float(data['Close'].iloc[i])
        roc = float(data['roc'].iloc[i])
        roc_ma = float(data['roc_ma'].iloc[i])
        mfi = float(data['mfi'].iloc[i])
        rsi = float(data['rsi'].iloc[i])
        volatility = float(data['volatility'].iloc[i])
        
        trade_date = data.index[i]
        current_trade_month = trade_date.month

        # Reset monthly loss tracker on new month
        if current_month != current_trade_month:
            current_month = current_trade_month
            monthly_loss = 0.0

        risk_config = risk_profiles[risk_tolerance]

        # Enhanced buy conditions with trend confirmation
        buy_condition = (
            roc > 2 and  # Strong momentum
            roc_ma > 0 and  # Confirmed uptrend
            (mfi < 40 or rsi < 35) and  # Conservative oversold levels
            position == 0 and  # No existing position
            monthly_loss > -risk_config['max_monthly_loss']  # Within monthly loss limit
        )

        # Update trailing stop if in position
        if position > 0 and close_price > peak_price:
            peak_price = close_price
            trailing_stop = peak_price * (1 - risk_config['trailing_stop'])

        # Enhanced sell conditions with trailing stop
        sell_condition = (
            position > 0 and (
                (roc < -2 and mfi > 70 and rsi > 70) or  # Strong overbought
                close_price <= trailing_stop or  # Trailing stop hit
                close_price >= entry_price * (1 + risk_config['take_profit_2'])  # Final take profit
            )
        )

        # Partial profit taking condition
        partial_profit_condition = (
            position > 0 and
            not partial_position and
            close_price >= entry_price * (1 + risk_config['take_profit_1'])
        )

        print(f"Date: {trade_date}, Close: {close_price}, ROC: {roc}, MFI: {mfi}, RSI: {rsi}")
        print(f"Buy Condition: {buy_condition}, Sell Condition: {sell_condition}")

        if buy_condition:
            # Position sizing based on volatility
            volatility_factor = 1 - (volatility * 10)  # Reduce position size in high volatility
            volatility_factor = max(0.3, min(1, volatility_factor))  # Limit between 0.3 and 1
            
            max_position_value = capital * risk_config['allocation'] * volatility_factor
            position_size = max_position_value / close_price
            
            capital -= max_position_value
            fee = max_position_value * fee_percentage
            capital -= fee
            position = position_size
            entry_price = close_price
            peak_price = close_price
            trailing_stop = peak_price * (1 - risk_config['initial_stop'])

            trades.append({
                "action": "BUY",
                "date": trade_date,
                "price": close_price,
                "entry_price": close_price,
                "capital_left": capital,
                "position": position,
                "indicators": {
                    "roc": round(roc, 2),
                    "roc_ma": round(roc_ma, 2),
                    "mfi": round(mfi, 2),
                    "rsi": round(rsi, 2),
                    "volatility": round(volatility, 4)
                },
                "reasons": {
                    "momentum": "Strong momentum with ROC > 2",
                    "trend": "Confirmed uptrend with positive ROC MA",
                    "oversold": "MFI below 40 or RSI below 35",
                    "position_size": f"Volatility adjustment: {round(volatility_factor, 2)}"
                }
            })

        elif partial_profit_condition:
            # Sell half position at first take profit level
            sell_size = position / 2
            sell_value = sell_size * close_price
            capital += sell_value
            fee = sell_value * fee_percentage
            capital -= fee
            position -= sell_size
            partial_position = True
            
            profit_loss = ((close_price - entry_price) / entry_price) * 100

            trades.append({
                "action": "PARTIAL_SELL",
                "date": trade_date,
                "price": close_price,
                "entry_price": entry_price,
                "exit_price": close_price,
                "profit_loss_percentage": round(profit_loss, 2),
                "capital_left": capital,
                "position": position,
                "indicators": {
                    "roc": round(roc, 2),
                    "roc_ma": round(roc_ma, 2),
                    "mfi": round(mfi, 2),
                    "rsi": round(rsi, 2)
                },
                "reasons": {
                    "take_profit": f"First target reached at {risk_config['take_profit_1'] * 100}%"
                }
            })

        elif sell_condition and position > 0:
            sell_value = position * close_price
            capital += sell_value
            fee = sell_value * fee_percentage
            capital -= fee
            profit_loss = ((close_price - entry_price) / entry_price) * 100
            
            # Update monthly loss tracker
            if profit_loss < 0:
                monthly_loss += profit_loss

            trades.append({
                "action": "SELL",
                "date": trade_date,
                "price": close_price,
                "entry_price": entry_price,
                "exit_price": close_price,
                "profit_loss_percentage": round(profit_loss, 2),
                "capital_left": capital,
                "position": 0,
                "indicators": {
                    "roc": round(roc, 2),
                    "roc_ma": round(roc_ma, 2),
                    "mfi": round(mfi, 2),
                    "rsi": round(rsi, 2)
                },
                "reasons": {
                    "momentum": "Strong downward momentum" if roc < -2 else None,
                    "overbought": "MFI and RSI overbought" if mfi > 70 and rsi > 70 else None,
                    "trailing_stop": close_price <= trailing_stop,
                    "take_profit": close_price >= entry_price * (1 + risk_config['take_profit_2'])
                }
            })
            
            position = 0.0
            entry_price = 0.0
            peak_price = 0.0
            trailing_stop = 0.0
            partial_position = False

    return trades, calculate_performance_metrics(initial_capital, capital, trades)