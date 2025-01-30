import numpy as np
import pandas as pd
from collections import defaultdict





def calculate_performance_metrics(initial_capital, final_capital, trades):
    """Calculate comprehensive trading performance metrics with Monte Carlo simulation."""
    metrics = {
        'returns': {},
        'risk': {},
        'trade_analysis': {},
        'time_analysis': {},
        'money_management': {},
        'simulations': {}
    }

    if not trades:
        return metrics

    # Convert trades to DataFrame for vectorized operations
    trades_df = pd.DataFrame(trades)
    trades_df['date'] = pd.to_datetime(trades_df['date'])
    trades_df = trades_df.sort_values('date').reset_index(drop=True)
    
    # Calculate equity curve and drawdowns
    equity_curve = [initial_capital]
    drawdowns = []
    peak = initial_capital
    in_position = False
    entry_idx = 0

    # Trade sequence analysis
    wins = []
    losses = []
    holding_periods = []
    monthly_returns = defaultdict(list)
    annual_returns = defaultdict(float)
    trade_profits = []
    consecutive_losses = []
    current_streak = 0

    for i, trade in trades_df.iterrows():
        if trade['action'] == 'BUY':
            equity_curve.append(equity_curve[-1] - trade['size'] * trade['price'] - trade.get('fee', 0))
            in_position = True
            entry_idx = i
            entry_date = trade['date']
        elif trade['action'] == 'SELL' and in_position:
            # Calculate position duration
            exit_date = trade['date']
            holding_days = (exit_date - entry_date).days
            holding_periods.append(holding_days)
            
            # Calculate PnL
            entry_trade = trades_df.iloc[entry_idx]
            pnl = trade['size'] * (trade['price'] - entry_trade['price'])
            pnl_pct = (trade['price'] / entry_trade['price'] - 1) * 100
            trade_profits.append(pnl_pct)
            
            # Update equity curve
            equity = equity_curve[-1] + pnl - trade.get('fee', 0)
            equity_curve.append(equity)
            
            # Track wins/losses
            if pnl_pct > 0:
                wins.append(pnl_pct)
                current_streak = max(current_streak - 1, 0)
            else:
                losses.append(pnl_pct)
                current_streak += 1
                consecutive_losses.append(current_streak)
            
            # Track monthly/annual returns
            year_month = exit_date.strftime("%Y-%m")
            monthly_returns[year_month].append(pnl_pct)
            annual_returns[exit_date.year] += pnl
            
            # Calculate drawdown
            peak = max(peak, equity)
            drawdown = (peak - equity) / peak * 100
            drawdowns.append(drawdown)
            in_position = False

    # Handle final position if any
    if in_position:
        final_trade = trades_df.iloc[-1]
        equity_curve.append(equity_curve[-1] + final_trade['size'] * final_trade['price'] - final_trade.get('fee', 0))

    # Convert to numpy arrays for vector operations
    trade_profits = np.array(trade_profits)
    wins = np.array(wins)
    losses = np.array(losses)
    drawdowns = np.array(drawdowns)
    holding_periods = np.array(holding_periods)

    # Returns analysis
    total_return_pct = (final_capital - initial_capital) / initial_capital * 100
    cagr = ((final_capital / initial_capital) ** (365.25 / (holding_periods.sum() or 1)) - 1) * 100
    sharpe_ratio = np.mean(trade_profits) / np.std(trade_profits) if len(trade_profits) > 1 else 0
    sortino_ratio = np.mean(trade_profits) / np.std(losses) if losses.size > 0 else 0

    # Risk metrics
    max_drawdown = np.max(drawdowns) if drawdowns.size > 0 else 0
    avg_drawdown = np.mean(drawdowns) if drawdowns.size > 0 else 0
    ulcer_index = np.sqrt(np.mean(drawdowns**2)) if drawdowns.size > 0 else 0

    # Trade analysis
    win_rate = len(wins) / len(trade_profits) * 100 if trade_profits.size > 0 else 0
    profit_factor = abs(wins.sum() / losses.sum()) if losses.size > 0 else 0
    expectancy = (np.mean(wins) * win_rate/100 + np.mean(losses) * (1 - win_rate/100)) if trade_profits.size > 0 else 0

    # Money management
    kelly = (win_rate/100 - (1 - win_rate/100)/abs(np.mean(wins)/np.mean(losses))) if losses.size > 0 else 0
    optimal_f = (abs(np.mean(wins)/abs(np.mean(losses))) * win_rate/100 - (1 - win_rate/100)) if losses.size > 0 else 0

    var_95 = 0.0
    cvar_95 = 0.0
    mc_returns = np.array([])
    if len(trade_profits) > 0:
        np.random.seed(42)
        mc_returns = []
        for _ in range(1000):
            random_walk = np.random.choice(trade_profits, size=len(trade_profits), replace=True)
            mc_returns.append(np.prod(1 + random_walk/100) - 1)
        
        # Convert to numpy array for vector operations
        mc_returns = np.array(mc_returns)
        var_95 = np.percentile(mc_returns, 5) * 100
        cvar_95 = np.mean(mc_returns[mc_returns <= np.percentile(mc_returns, 5)]) * 100

    # Modified metrics population with native float conversion
    metrics['returns'] = {
        'total_return_pct': float(round(total_return_pct, 2)),
        'cagr_pct': float(round(cagr, 2)),
        'sharpe_ratio': float(round(sharpe_ratio, 2)),
        'sortino_ratio': float(round(sortino_ratio, 2)),
        'best_month_pct': float(round(max([sum(m) for m in monthly_returns.values()], default=0), 2)),
        'worst_month_pct': float(round(min([sum(m) for m in monthly_returns.values()], default=0), 2)),
        'annualized_volatility_pct': float(round(np.std(trade_profits) * np.sqrt(252), 2)) if trade_profits.size > 0 else 0.0
    }

    metrics['risk'] = {
        'max_drawdown_pct': float(round(max_drawdown, 2)),
        'avg_drawdown_pct': float(round(avg_drawdown, 2)) if drawdowns.size > 0 else 0.0,
        'ulcer_index': float(round(ulcer_index, 2)),
        'var_95_pct': float(round(var_95, 2)) if len(mc_returns) > 0 else 0.0,
        'cvar_95_pct': float(round(cvar_95, 2)) if len(mc_returns) > 0 else 0.0
    }

    metrics['trade_analysis'] = {
        'win_rate_pct': float(round(win_rate, 2)),
        'profit_factor': float(round(profit_factor, 2)),
        'expectancy_pct': float(round(expectancy, 2)),
        'avg_win_pct': float(round(np.mean(wins), 2)) if wins.size > 0 else 0.0,
        'avg_loss_pct': float(round(np.mean(losses), 2)) if losses.size > 0 else 0.0,
        'max_win_pct': float(round(np.max(wins), 2)) if wins.size > 0 else 0.0,
        'max_loss_pct': float(round(np.min(losses), 2)) if losses.size > 0 else 0.0,
        'risk_reward_ratio': float(round(abs(np.mean(wins)/np.mean(losses)), 2)) if wins.size > 0 and losses.size > 0 else 0.0
    }

    metrics['time_analysis'] = {
        'avg_holding_days': float(round(np.mean(holding_periods), 1)) if holding_periods.size > 0 else 0.0,
        'median_holding_days': float(round(np.median(holding_periods), 1)) if holding_periods.size > 0 else 0.0,
        'max_holding_days': int(round(np.max(holding_periods), 0)) if holding_periods.size > 0 else 0,
        'trades_per_year': float(round(len(trades)/(len(annual_returns) or 1), 1)),
        'best_year_pct': float(round(max(annual_returns.values())/initial_capital*100, 2)) if annual_returns else 0.0,
        'worst_year_pct': float(round(min(annual_returns.values())/initial_capital*100, 2)) if annual_returns else 0.0
    }

    metrics['money_management'] = {
        'kelly_criterion_pct': float(round(kelly * 100, 1)),
        'optimal_f_pct': float(round(optimal_f * 100, 1)),
        'max_consecutive_losses': int(max(consecutive_losses, default=0)),
        'avg_position_size_pct': float(round((np.mean(trades_df[trades_df['action'] == 'BUY']['size']) / initial_capital) * 100, 1)) if 'size' in trades_df else 0.0
    }

    metrics['simulations'] = {
        'monte_carlo_positive_pct': float(round(len([r for r in mc_returns if r > 0])/len(mc_returns)*100, 2)) if len(mc_returns) > 0 else 0.0,
        'best_simulation_pct': float(round(np.max(mc_returns)*100, 2)) if len(mc_returns) > 0 else 0.0,
        'worst_simulation_pct': float(round(np.min(mc_returns)*100, 2)) if len(mc_returns) > 0 else 0.0
    }


