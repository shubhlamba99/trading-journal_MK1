import pandas as pd
import os
from datetime import datetime

DB_FILE = "trade_journal.xlsx"

COLUMNS = [
    "Trade_ID", "Trade_Status",
    # Entry Fields
    "Entry_Date", "Symbol", "Strategy", "Direction",
    "Lots", "Width", "Credit_Received", "Max_Loss", "Margin_Used", "DTE_Entry",
    "Spread_Entry_Price",
    "Short_Leg_Entry", "Long_Leg_Entry",
    "Short_Call_Entry", "Long_Call_Entry", "Short_Put_Entry", "Long_Put_Entry",
    "Sell_Strike_Delta",
    "IV_Entry", "IV_Percentile_Entry", "IV_HV_Percent", "VIX_Entry",
    "Planned_Exit_Percent", "Entry_Confidence",
    # Exit Fields
    "Exit_Date", "Spread_Exit_Price",
    "Short_Leg_Exit", "Long_Leg_Exit",
    "Short_Call_Exit", "Long_Call_Exit", "Short_Put_Exit", "Long_Put_Exit",
    "Adjustment_Made", "Exit_Emotion", "Rule_Broken", "Rule_Broken_Which",
    # Calculated Fields
    "Days_in_Trade", "Multiplier", "Realized_PnL", "Win_Loss",
    "Return_on_Margin_%", "Yield_per_Trade", "Max_Profit",
    "Exit_Efficiency_%", "Risk_Utilization_%", "Rule_Violation_Flag"
]

def initialize_db():
    """Creates the Excel file with headers if it doesn't exist."""
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_excel(DB_FILE, index=False)
        print(f"Created {DB_FILE}")
    else:
        # Check if columns match, if not, we might need to handle migration, but for now just assume it's correct or print warning
        # In a strict environment, we'd validate headers.
        pass

def load_db():
    """Loads the database into a DataFrame."""
    if not os.path.exists(DB_FILE):
        initialize_db()
    return pd.read_excel(DB_FILE)

def save_db(df):
    """Saves the DataFrame to the Excel file."""
    df.to_excel(DB_FILE, index=False)

def save_new_trade(trade_data):
    """
    Appends a new trade to the database.
    trade_data: dict containing entry fields.
    """
    df = load_db()
    
    # Generate Trade_ID
    if df.empty:
        new_id = 1
    else:
        # simple incremental ID. 
        # Convert Trade_ID to numeric to find max, handling potential non-numeric issues if manual edits happened
        df['Trade_ID'] = pd.to_numeric(df['Trade_ID'], errors='coerce')
        new_id = df['Trade_ID'].max() + 1
        if pd.isna(new_id):
            new_id = 1
            
    trade_data['Trade_ID'] = int(new_id)
    trade_data['Trade_Status'] = "OPEN"
    
    # Ensure all columns are present in trade_data, fill missing with None
    row_data = {col: trade_data.get(col, None) for col in COLUMNS}
    
    # Convert to DataFrame and append
    new_row = pd.DataFrame([row_data])
    df = pd.concat([df, new_row], ignore_index=True)
    
    save_db(df)
    return new_id

def get_open_trades():
    """Returns a DataFrame of trades with Trade_Status == 'OPEN'."""
    df = load_db()
    if df.empty:
        return df
    return df[df['Trade_Status'] == 'OPEN']

def get_closed_trades():
    """Returns a DataFrame of trades with Trade_Status == 'CLOSED'."""
    df = load_db()
    if df.empty:
        return df
    return df[df['Trade_Status'] == 'CLOSED']

def update_trade_to_closed(trade_id, exit_data, computed_metrics):
    """
    Updates a specific trade to CLOSED with exit data and computed metrics.
    trade_id: The ID of the trade to update.
    exit_data: dict of exit fields.
    computed_metrics: dict of calculated fields.
    """
    df = load_db()
    
    # Find the index of the trade
    mask = df['Trade_ID'] == trade_id
    if not mask.any():
        raise ValueError(f"Trade ID {trade_id} not found.")
        
    idx = df.index[mask][0]
    
    # Update fields
    for key, value in exit_data.items():
        if key in COLUMNS:
            df.at[idx, key] = value
            
    for key, value in computed_metrics.items():
        if key in COLUMNS:
            df.at[idx, key] = value
            
    df.at[idx, 'Trade_Status'] = "CLOSED"
    
    save_db(df)
