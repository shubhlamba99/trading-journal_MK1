import pandas as pd
from analytics import calculate_trade_metrics, calculate_portfolio_metrics

def test_analytics():
    print("Testing calculate_trade_metrics...")
    trade_row = {
        'Entry_Date': '2023-01-01',
        'Lots': 1,
        'Spread_Entry_Price': 2.00,
        'Credit_Received': 2.00,
        'Max_Loss': 300,
        'Margin_Used': 300
    }
    exit_data = {
        'Exit_Date': '2023-01-10',
        'Spread_Exit_Price': 1.00
    }
    
    # Expected: 
    # PnL = (2.00 - 1.00) * 1 * 100 = 100
    # Days = 9
    # Max Profit = 2.00 * 1 * 100 = 200
    # ROI = 100 / 300 = 33.33%
    
    metrics = calculate_trade_metrics(trade_row, exit_data)
    
    assert metrics['Realized_PnL'] == 100.0
    assert metrics['Days_in_Trade'] == 9
    assert metrics['Max_Profit'] == 200.0
    assert abs(metrics['Return_on_Margin_%'] - 33.333) < 0.01
    print("Trade metrics passed.")
    
    print("Testing calculate_portfolio_metrics...")
    # Create dummy dataframe
    data = {
        'Exit_Date': [pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-02'), pd.Timestamp('2023-01-03')],
        'Realized_PnL': [100, -50, 200]
    }
    df = pd.DataFrame(data)
    
    # Cumulative: 100, 50, 250.
    # Peak: 100, 100, 250.
    # DD: 0, -50, 0.
    # Max DD: -50.
    # Wins: 2, Losses: 1.
    # WinRate: 2/3 = 0.666
    # AvgWin: 150
    # AvgLoss: 50
    # Expectancy: (0.66 * 150) - (0.33 * 50) = 100 - 16.6 = ~83.33
    
    p_metrics = calculate_portfolio_metrics(df)
    
    assert p_metrics['Cumulative_PnL'] == 250
    assert p_metrics['Max_Drawdown'] == -50
    assert abs(p_metrics['Expectancy'] - 83.333) < 0.1
    print("Portfolio metrics passed.")

if __name__ == "__main__":
    test_analytics()
