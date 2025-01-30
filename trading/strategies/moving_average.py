import pandas as pd
import numpy as np
from ..metrics import calculate_performance_metrics

def MovingAverage(data, initial_capital, risk_tolerance, fee_percentage, ticker, 
                 short_window=10, long_window=30, min_volume=1e6):
    """
    Enhanced moving average crossover strategy with:
    - Manual RSI calculation
    - Dynamic ATR-based stops
    - Modified entry conditions based on real market behavior
    - Flexible entry criteria with weighted conditions
    
    Parameters:
    -----------
    data : pandas.DataFrame
        OHLCV data with columns: Open, High, Low, Close, Volume
    initial_capital : float
        Starting capital for the strategy
    risk_tolerance : str
        One of 'High', 'Moderate', or 'Low'
    fee_percentage : float
        Trading fee as a percentage
    ticker : str
        Symbol being traded
    short_window : int, optional
        Short-term MA period (default: 10)
    long_window : int, optional
        Long-term MA period (default: 30)
    min_volume : float, optional
        Minimum volume threshold (default: 1e6)
    """
    # Debug prints to verify input parameters
    print(f"Strategy Parameters:")
    print(f"Initial Capital: {initial_capital}")
    print(f"Risk Tolerance: {risk_tolerance}")
    print(f"Fee Percentage: {fee_percentage}")
    print(f"Short Window: {short_window}")
    print(f"Long Window: {long_window}")
    
    capital = float(initial_capital)
    position = 0.0
    entry_price = 0.0
    monthly_trades = 0
    current_year_month = None
    trades = []
    
    risk_profiles = {
        'High': {
            'allocation': 0.8,
            'stop_loss': 0.06,
            'trailing_stop': 0.04,
            'max_monthly_trades': 3,
            'min_holding_days': 5,
            'trend_lookback': 5
        },
        'Moderate': {
            'allocation': 0.5,
            'stop_loss': 0.05,
            'trailing_stop': 0.04,
            'max_monthly_trades': 3,
            'min_holding_days': 7,
            'trend_lookback': 10
        },
        'Low': {
            'allocation': 0.3,
            'stop_loss': 0.04,
            'trailing_stop': 0.03,
            'max_monthly_trades': 2,
            'min_holding_days': 10,
            'trend_lookback': 15
        }
    }

    if risk_tolerance not in risk_profiles:
        raise ValueError(f"Invalid risk tolerance: {risk_tolerance}. Use 'High', 'Moderate', or 'Low'.")

    # Prepare DataFrame and indicators
    df = data.copy()
    required_cols = ['Close', 'High', 'Low', 'Volume']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"Data must contain {', '.join(required_cols)} columns")
    
    print(f"Data shape before calculations: {df.shape}")
    
    # Moving Averages
    df['short_ma'] = df['Close'].rolling(window=short_window, min_periods=1).mean()
    df['long_ma'] = df['Close'].rolling(window=long_window, min_periods=1).mean()
    
    # Volatility (ATR)
    df['tr'] = np.maximum(
        df['High'] - df['Low'],
        np.maximum(
            abs(df['High'] - df['Close'].shift(1)),
            abs(df['Low'] - df['Close'].shift(1))
        )
    )
    df['atr'] = df['tr'].rolling(window=14, min_periods=1).mean()
    
    # Volume Analysis
    df['volume_ma'] = df['Volume'].rolling(window=20, min_periods=1).mean()
    df['volume_ratio'] = df['Volume'] / df['volume_ma']
    
    # Trend Confirmation
    config = risk_profiles[risk_tolerance]
    lookback = config['trend_lookback']
    df['long_ma_trend'] = df['long_ma'].rolling(window=lookback + 1).apply(
        lambda x: 1 if x.iloc[-1] > x.iloc[0] else 0, raw=False
    )
    
    # Manual RSI Calculation
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    
    avg_loss = avg_loss.replace(0, np.nan)
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))
    df['rsi'] = df['rsi'].ffill().fillna(50)
    
    # Handle NaN values
    df = df.ffill().bfill()
    
    print(f"Data shape after calculations: {df.shape}")
    print(f"Sample of calculated indicators:")
    print(df[['Close', 'short_ma', 'long_ma', 'rsi', 'volume_ratio']].head())
    
    if len(df) < 2:
        return [], calculate_performance_metrics(initial_capital, initial_capital, [])
    
    # Trading Logic
    highest_price = 0
    days_in_trade = 0
    
    for i in range(1, len(df)):
        trade_date = df.index[i]
        year_month = (trade_date.year, trade_date.month)
        
        if year_month != current_year_month:
            current_year_month = year_month
            monthly_trades = 0
        
        close_price = df['Close'].iloc[i]
        high_price = df['High'].iloc[i]
        volume = df['Volume'].iloc[i]
        short_ma = df['short_ma'].iloc[i]
        long_ma = df['long_ma'].iloc[i]
        prev_short_ma = df['short_ma'].iloc[i-1]
        prev_long_ma = df['long_ma'].iloc[i-1]
        volume_ratio = df['volume_ratio'].iloc[i]
        long_ma_trend = bool(df['long_ma_trend'].iloc[i])
        current_atr = df['atr'].iloc[i]
        current_rsi = df['rsi'].iloc[i]
        
        # Update highest price in trade
        if position > 0 and close_price > highest_price:
            highest_price = close_price
        
        # Buy Signal with adjusted filters
        if position == 0:
            # Check for MA crossover with confirmation
            ma_crossover = (short_ma > long_ma) and (prev_short_ma <= prev_long_ma)
            
            # Modified entry conditions
            trend_ok = close_price > long_ma
            
            # Volume condition with reduced threshold
            volume_ok = volume_ratio > 1.0
            
            # RSI with wider range
            rsi_ok = 30 <= current_rsi <= 65
            
            # Modified pullback logic with ATR
            atr_multiplier = 2.0
            recent_swing = df['High'].iloc[i-5:i].max()
            pullback_threshold = recent_swing - (current_atr * atr_multiplier)
            pullback_ok = close_price < pullback_threshold or close_price < (0.99 * recent_swing)
            
            # Additional trend strength check
            trend_strength = df['Close'].iloc[i-5:i].mean() > df['Close'].iloc[i-10:i-5].mean()
            
            if ma_crossover:
                print(f"Signal conditions on {trade_date}:")
                print(f"MA Crossover: {ma_crossover}")
                print(f"Volume OK: {volume_ok} (ratio: {volume_ratio:.2f})")
                print(f"Trend OK: {trend_ok} & Strength: {trend_strength}")
                print(f"RSI OK: {rsi_ok} (RSI: {current_rsi:.2f})")
                print(f"Pullback OK: {pullback_ok} (ATR mult: {atr_multiplier})")
            
            # Combined entry conditions with flexibility
            entry_conditions = [
                ma_crossover,
                trend_ok,
                trend_strength,
                (volume_ok or current_rsi < 40),  # Allow lower volume if RSI shows oversold
                (pullback_ok or (current_rsi < 35)),  # Allow entry without pullback if very oversold
                rsi_ok
            ]
            
            if sum(entry_conditions) >= 4:  # Allow entry if most conditions are met
                if monthly_trades < config['max_monthly_trades']:
                    risk_amount = capital * config['allocation']
                    position_size = risk_amount / close_price
                    trade_cost = position_size * close_price
                    fee = trade_cost * fee_percentage
                    
                    if (trade_cost + fee) <= capital:
                        capital -= (trade_cost + fee)
                        position = position_size
                        entry_price = close_price
                        highest_price = close_price
                        days_in_trade = 0
                        monthly_trades += 1
                        
                        trades.append({
                            "action": "BUY",
                            "date": trade_date.strftime("%Y-%m-%d"),
                            "price": round(close_price, 2),
                            "size": round(position_size, 4),
                            "position": round(position_size, 4),
                            "capital_remaining": round(capital, 2),
                            "reasons": {
                                "reason": "MA Crossover with Enhanced Filters",
                                "volume_ratio": round(volume_ratio, 2),
                                "rsi": round(current_rsi, 2),
                                "conditions_met": sum(entry_conditions),
                                "trend_strength": trend_strength,
                                "risk_allocated": round(risk_amount, 2)
                            }
                        })
        
        elif position > 0:
            sell_reasons = []
            
            # Calculate dynamic stop levels
            hard_stop = entry_price * (1 - config['stop_loss'])
            trailing_stop = highest_price * (1 - config['trailing_stop'])
            atr_stop = close_price - (2 * current_atr)
            dynamic_stop = max(hard_stop, trailing_stop, atr_stop)
            
            if close_price <= dynamic_stop:
                if close_price <= hard_stop:
                    sell_reasons.append(f"Hard Stop ({config['stop_loss']*100}%)")
                if close_price <= trailing_stop:
                    sell_reasons.append(f"Trailing Stop ({config['trailing_stop']*100}%)")
                if close_price <= atr_stop:
                    sell_reasons.append(f"ATR Stop (2x ATR: {round(2*current_atr, 2)})")
            
            if (days_in_trade >= config['min_holding_days']) and (close_price < long_ma):
                sell_reasons.append(f"Holding Period ({days_in_trade}d) & Below MA")
            
            if sell_reasons:
                exit_value = position * close_price
                fee = exit_value * fee_percentage
                capital += (exit_value - fee)
                profit_pct = ((close_price - entry_price) / entry_price) * 100
                
                trades.append({
                    "action": "SELL",
                    "date": trade_date.strftime("%Y-%m-%d"),
                    "price": round(close_price, 2),
                    "size": round(position, 4),
                    "position": 0,
                    "profit_pct": round(profit_pct, 2),
                    "capital_remaining": round(capital, 2),
                    "reasons": {
                        "triggers": sell_reasons,
                        "days_held": days_in_trade,
                        "max_price": round(highest_price, 2),
                        "atr_exit": round(current_atr, 2),
                        "dynamic_stop": round(dynamic_stop, 2)
                    }
                })
                
                position = 0.0
                entry_price = 0.0
                highest_price = 0
        
        if position > 0:
            days_in_trade += 1
    
    # Close remaining position at the end
    if position > 0:
        close_price = df['Close'].iloc[-1]
        exit_value = position * close_price
        fee = exit_value * fee_percentage
        capital += (exit_value - fee)
        profit_pct = ((close_price - entry_price) / entry_price) * 100
        
        trades.append({
            "action": "SELL",
            "date": df.index[-1].strftime("%Y-%m-%d"),
            "price": round(close_price, 2),
            "size": round(position, 4),
            "position": 0,
            "profit_pct": round(profit_pct, 2),
            "capital_remaining": round(capital, 2),
            "reasons": {
                "triggers": ["End of Period"],
                "days_held": days_in_trade,
                "max_price": round(highest_price, 2)
            }
        })

    print(f"Total trades generated: {len(trades)}")
    return trades, calculate_performance_metrics(initial_capital, capital, trades)