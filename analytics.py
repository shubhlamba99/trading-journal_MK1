import pandas as pd
from datetime import datetime

def calculate_trade_metrics(trade_row, exit_data):
    """
    Calculates metrics for a single trade upon exit.
    
    trade_row: pandas Series or dict containing entry data.
    exit_data: dict containing user-provided exit data.
    
    Returns: dict of calculated metrics.
    """
    
    # Extract Entry Data
    entry_date = pd.to_datetime(trade_row['Entry_Date'])
    lots = float(trade_row['Lots'])
    spread_entry_price = float(trade_row['Spread_Entry_Price'])
    credit_received = float(trade_row['Credit_Received'])
    max_loss = float(trade_row['Max_Loss'])
    margin_used = float(trade_row['Margin_Used'])
    
    # Extract Exit Data
    exit_date = pd.to_datetime(exit_data['Exit_Date'])
    spread_exit_price = float(exit_data['Spread_Exit_Price'])
    
    # Constants
    MULTIPLIER = 100
    
    # Calculations
    days_in_trade = (exit_date - entry_date).days
    
    # Realized_PnL (SIGNED)
    # Formula: (Spread_Entry_Price − Spread_Exit_Price) × Lots × Multiplier
    # Since it's credit strategy (selling), profit is Entry - Exit.
    realized_pnl = (spread_entry_price - spread_exit_price) * lots * MULTIPLIER
    
    # Win_Loss
    win_loss = "Win" if realized_pnl > 0 else "Loss"
    
    # Return_on_Margin_%
    # Formula: (Realized_PnL / Margin_Used) × 100
    if margin_used != 0:
        return_on_margin = (realized_pnl / margin_used) * 100
    else:
        return_on_margin = 0.0
        
    # Yield_per_Trade
    # Formula: Realized_PnL / Margin_Used
    if margin_used != 0:
        yield_per_trade = realized_pnl / margin_used
    else:
        yield_per_trade = 0.0
        
    # Max_Profit
    # Formula: Credit_Received × Lots × Multiplier
    max_profit = credit_received * lots * MULTIPLIER
    
    # Exit_Efficiency_%
    # Formula: Realized_PnL / Max_Profit × 100
    if max_profit != 0:
        exit_efficiency = (realized_pnl / max_profit) * 100
    else:
        exit_efficiency = 0.0
        
    # Risk_Utilization_% (ALWAYS POSITIVE)
    # Formula: |Realized_PnL| / Max_Loss × 100
    if max_loss != 0:
        risk_utilization = (abs(realized_pnl) / max_loss) * 100
    else:
        risk_utilization = 0.0
        
    # Rule_Violation_Flag
    # 1 if Risk_Utilization_% > 60 else 0
    rule_violation_flag = 1 if risk_utilization > 60 else 0
    
    return {
        "Days_in_Trade": days_in_trade,
        "Multiplier": MULTIPLIER,
        "Realized_PnL": realized_pnl,
        "Win_Loss": win_loss,
        "Return_on_Margin_%": return_on_margin,
        "Yield_per_Trade": yield_per_trade,
        "Max_Profit": max_profit,
        "Exit_Efficiency_%": exit_efficiency,
        "Risk_Utilization_%": risk_utilization,
        "Rule_Violation_Flag": rule_violation_flag
    }

def calculate_portfolio_metrics(df_closed):
    """
    Calculates portfolio-level analytics for closed trades.
    
    df_closed: DataFrame of closed trades.
    
    Returns: dict of metrics.
    """
    if df_closed.empty:
        return {
            "Cumulative_PnL": 0.0,
            "Drawdown": 0.0,
            "Max_Drawdown": 0.0,
            "Expectancy": 0.0,
            "Win_Rate": 0.0,
            "Total_Trades": 0
        }
        
    # Cumulative PnL
    cumulative_pnl = df_closed['Realized_PnL'].sum()
    
    # Equity Curve (represented as cumulative sum series)
    # We won't return the full series here unless needed for plotting, 
    # but we need it for Drawdown calculations.
    # Ensure sorted by Exit Date
    df_sorted = df_closed.sort_values(by='Exit_Date')
    equity_curve = df_sorted['Realized_PnL'].cumsum()
    
    # Drawdown
    # DD = Peak - Current. But strictly speaking, it's usually relative to Peak Equity.
    # Assuming starting equity is 0 or just tracking PnL drawdown.
    # Let's assume PnL drawdown from peak accumulated PnL.
    running_max = equity_curve.cummax()
    drawdown = equity_curve - running_max
    
    current_drawdown = drawdown.iloc[-1]
    max_drawdown = drawdown.min() # Most negative value
    
    # Expectancy
    # (WinRate × AvgWin) − (LossRate × AvgLoss)
    wins = df_closed[df_closed['Realized_PnL'] > 0]
    losses = df_closed[df_closed['Realized_PnL'] <= 0]
    
    total_trades = len(df_closed)
    win_rate = len(wins) / total_trades if total_trades > 0 else 0
    loss_rate = len(losses) / total_trades if total_trades > 0 else 0
    
    avg_win = wins['Realized_PnL'].mean() if not wins.empty else 0
    avg_loss = abs(losses['Realized_PnL'].mean()) if not losses.empty else 0 # Use absolute for formula subtraction if using minus
    
    # Formula: (WinRate * AvgWin) - (LossRate * AvgLoss)
    expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
    
    return {
        "Cumulative_PnL": cumulative_pnl,
        "Equity_Curve": equity_curve.tolist(),
        "Drawdown": current_drawdown,
        "Max_Drawdown": max_drawdown,
        "Expectancy": expectancy,
        "Win_Rate": win_rate * 100, # Percentage
        "Total_Trades": total_trades
    }
