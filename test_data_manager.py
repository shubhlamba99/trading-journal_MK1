import os
import pandas as pd
from data_manager import initialize_db, save_new_trade, get_open_trades, update_trade_to_closed, load_db, DB_FILE

def test_data_manager():
    # Setup: Remove existing DB
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        
    print("Testing initialize_db...")
    initialize_db()
    assert os.path.exists(DB_FILE)
    
    print("Testing save_new_trade...")
    entry_data = {
        "Entry_Date": "2023-10-27",
        "Symbol": "SPX",
        "Strategy": "Iron Condor",
        "Direction": "Neutral",
        "Lots": 1,
        "Spread_Entry_Price": 5.00
    }
    trade_id = save_new_trade(entry_data)
    print(f"Trade saved with ID: {trade_id}")
    
    print("Testing get_open_trades...")
    open_trades = get_open_trades()
    assert len(open_trades) == 1
    assert open_trades.iloc[0]['Symbol'] == "SPX"
    assert open_trades.iloc[0]['Trade_Status'] == "OPEN"
    
    print("Testing update_trade_to_closed...")
    exit_data = {
        "Exit_Date": "2023-11-01",
        "Spread_Exit_Price": 2.00
    }
    computed_metrics = {
        "Realized_PnL": 300.00
    }
    update_trade_to_closed(trade_id, exit_data, computed_metrics)
    
    df = load_db()
    trade = df[df['Trade_ID'] == trade_id].iloc[0]
    assert trade['Trade_Status'] == "CLOSED"
    assert trade['Spread_Exit_Price'] == 2.00
    assert trade['Realized_PnL'] == 300.00
    
    print("All tests passed!")

if __name__ == "__main__":
    test_data_manager()
