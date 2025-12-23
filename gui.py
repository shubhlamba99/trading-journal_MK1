import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import data_manager
import analytics

class TradeJournalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trade Journal")
        self.root.geometry("1000x700")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Tabs
        self.tab_control = ttk.Notebook(root)
        
        self.tab_entry = ttk.Frame(self.tab_control)
        self.tab_manage = ttk.Frame(self.tab_control)
        self.tab_analytics = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_entry, text='New Trade')
        self.tab_control.add(self.tab_manage, text='Open Trades')
        self.tab_control.add(self.tab_analytics, text='Analytics')
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Initialize Tabs
        self.setup_entry_tab()
        self.setup_manage_tab()
        self.setup_analytics_tab()
        
        # Bind tab change to refresh
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        
        if tab_text == "Open Trades":
            self.refresh_open_trades()
        elif tab_text == "Analytics":
            self.refresh_analytics()

    def setup_entry_tab(self):
        frame = ttk.Frame(self.tab_entry, padding="10")
        frame.pack(fill="both", expand=True)
        
        # Create Canvas for scrolling if needed, but for now just grid
        # Use a LabelFrame for grouping
        
        # --- Basic Info ---
        basic_frame = ttk.LabelFrame(frame, text="Trade Basics", padding="5")
        basic_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Label(basic_frame, text="Entry Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
        self.entry_date = ttk.Entry(basic_frame)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_date.grid(row=0, column=1)
        
        ttk.Label(basic_frame, text="Symbol:").grid(row=0, column=2, sticky="w")
        self.symbol = ttk.Entry(basic_frame)
        self.symbol.grid(row=0, column=3)
        
        ttk.Label(basic_frame, text="Strategy:").grid(row=1, column=0, sticky="w")
        self.strategy = ttk.Combobox(basic_frame, values=["Credit Spread", "Iron Condor"], state="readonly")
        self.strategy.grid(row=1, column=1)
        self.strategy.bind("<<ComboboxSelected>>", self.update_leg_fields)
        
        ttk.Label(basic_frame, text="Direction:").grid(row=1, column=2, sticky="w")
        self.direction = ttk.Combobox(basic_frame, values=["Neutral", "Bullish", "Bearish"], state="readonly")
        self.direction.grid(row=1, column=3)
        
        # --- Structure & Risk ---
        risk_frame = ttk.LabelFrame(frame, text="Structure & Risk", padding="5")
        risk_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        fields = [("Lots", "lots"), ("Width", "width"), ("Credit Received", "credit"), 
                  ("Max Loss", "max_loss"), ("Margin Used", "margin"), ("DTE Entry", "dte"),
                  ("Spread Entry Price", "spread_price")]
        
        self.entry_vars = {}
        for i, (label, key) in enumerate(fields):
            r, c = divmod(i, 4)
            ttk.Label(risk_frame, text=f"{label}:").grid(row=r*2, column=c, sticky="w")
            var = ttk.Entry(risk_frame)
            var.grid(row=r*2+1, column=c, padx=5)
            self.entry_vars[key] = var

        # --- Legs (Dynamic) ---
        self.legs_frame = ttk.LabelFrame(frame, text="Leg Prices", padding="5")
        self.legs_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        # Placeholders for leg fields
        self.leg_widgets = {}
        
        # --- Market Context ---
        context_frame = ttk.LabelFrame(frame, text="Market Context", padding="5")
        context_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        
        c_fields = [("IV Entry", "iv"), ("IV Percentile", "iv_rank"), 
                    ("IV/HV %", "iv_hv"), ("VIX Entry", "vix")]
        for i, (label, key) in enumerate(c_fields):
            ttk.Label(context_frame, text=f"{label}:").grid(row=0, column=i, sticky="w")
            var = ttk.Entry(context_frame)
            var.grid(row=1, column=i, padx=5)
            self.entry_vars[key] = var
            
        # --- Discipline ---
        disc_frame = ttk.LabelFrame(frame, text="Discipline", padding="5")
        disc_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Label(disc_frame, text="Planned Exit %:").grid(row=0, column=0)
        self.entry_vars['plan_exit'] = ttk.Entry(disc_frame)
        self.entry_vars['plan_exit'].grid(row=0, column=1)
        
        ttk.Label(disc_frame, text="Entry Confidence (1-5):").grid(row=0, column=2)
        self.entry_vars['confidence'] = ttk.Combobox(disc_frame, values=[1,2,3,4,5], state="readonly")
        self.entry_vars['confidence'].grid(row=0, column=3)
        
        # Submit Button
        ttk.Button(frame, text="SAVE TRADE", command=self.save_trade).grid(row=5, column=0, pady=20)
        
        self.update_leg_fields() # Init state

    def update_leg_fields(self, event=None):
        # Clear existing leg widgets
        for widget in self.legs_frame.winfo_children():
            widget.destroy()
            
        strategy = self.strategy.get()
        self.leg_widgets = {}
        
        if strategy == "Credit Spread":
            labels = ["Short Leg Entry", "Long Leg Entry"]
            keys = ["Short_Leg_Entry", "Long_Leg_Entry"]
        elif strategy == "Iron Condor":
            labels = ["Short Call", "Long Call", "Short Put", "Long Put"]
            keys = ["Short_Call_Entry", "Long_Call_Entry", "Short_Put_Entry", "Long_Put_Entry"]
        else:
            labels = []
            keys = []
            
        for i, (label, key) in enumerate(zip(labels, keys)):
            ttk.Label(self.legs_frame, text=label).grid(row=0, column=i, padx=5)
            entry = ttk.Entry(self.legs_frame)
            entry.grid(row=1, column=i, padx=5)
            self.leg_widgets[key] = entry

    def save_trade(self):
        # Validation
        try:
            data = {
                "Entry_Date": self.entry_date.get(),
                "Symbol": self.symbol.get(),
                "Strategy": self.strategy.get(),
                "Direction": self.direction.get(),
                "Lots": float(self.entry_vars['lots'].get()),
                "Width": float(self.entry_vars['width'].get()),
                "Credit_Received": float(self.entry_vars['credit'].get()),
                "Max_Loss": float(self.entry_vars['max_loss'].get()),
                "Margin_Used": float(self.entry_vars['margin'].get()),
                "DTE_Entry": int(self.entry_vars['dte'].get()),
                "Spread_Entry_Price": float(self.entry_vars['spread_price'].get()),
                
                "IV_Entry": float(self.entry_vars['iv'].get() or 0),
                "IV_Percentile_Entry": float(self.entry_vars['iv_rank'].get() or 0),
                "IV_HV_Percent": float(self.entry_vars['iv_hv'].get() or 0),
                "VIX_Entry": float(self.entry_vars['vix'].get() or 0),
                
                "Planned_Exit_Percent": float(self.entry_vars['plan_exit'].get() or 0),
                "Entry_Confidence": int(self.entry_vars['confidence'].get() or 3)
            }
            
            # Add dynamic legs
            for key, widget in self.leg_widgets.items():
                val = widget.get()
                data[key] = float(val) if val else 0.0
            
            if not data['Symbol'] or not data['Strategy']:
                raise ValueError("Symbol and Strategy are required.")

            trade_id = data_manager.save_new_trade(data)
            messagebox.showinfo("Success", f"Trade saved with ID {trade_id}")
            
            # Clear fields (Optional, but good UX)
            self.symbol.delete(0, tk.END)
            # ... clear others ...
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid Input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"System Error: {e}")

    def setup_manage_tab(self):
        # Paned Window: Top list, Bottom form
        paned = ttk.PanedWindow(self.tab_manage, orient=tk.VERTICAL)
        paned.pack(fill="both", expand=True)
        
        # Top: Treeview
        list_frame = ttk.LabelFrame(paned, text="Open Trades")
        paned.add(list_frame, weight=1)
        
        cols = ("ID", "Date", "Symbol", "Strategy", "Lots", "Spread Price")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=8)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_trade_select)
        
        # Bottom: Exit Form
        self.exit_frame = ttk.LabelFrame(paned, text="Close Trade")
        paned.add(self.exit_frame, weight=3)
        
        # Exit Fields
        ttk.Label(self.exit_frame, text="Exit Date:").grid(row=0, column=0)
        self.exit_date = ttk.Entry(self.exit_frame)
        self.exit_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.exit_date.grid(row=0, column=1)
        
        ttk.Label(self.exit_frame, text="Spread Exit Price:").grid(row=0, column=2)
        self.exit_price = ttk.Entry(self.exit_frame)
        self.exit_price.grid(row=0, column=3)
        
        # Legs Exit (Dynamic based on selection)
        self.exit_legs_frame = ttk.Frame(self.exit_frame)
        self.exit_legs_frame.grid(row=1, column=0, columnspan=4, pady=10)
        self.exit_leg_widgets = {}
        
        # Discipline
        ttk.Label(self.exit_frame, text="Adjustment:").grid(row=2, column=0)
        self.adj = ttk.Combobox(self.exit_frame, values=["None", "Roll", "Hedge"])
        self.adj.grid(row=2, column=1)
        
        ttk.Label(self.exit_frame, text="Emotion:").grid(row=2, column=2)
        self.emo = ttk.Combobox(self.exit_frame, values=["Calm", "Fear", "Greed"])
        self.emo.grid(row=2, column=3)
        
        ttk.Label(self.exit_frame, text="Rule Broken?").grid(row=3, column=0)
        self.rule = ttk.Combobox(self.exit_frame, values=["No", "Yes"])
        self.rule.grid(row=3, column=1)
        
        ttk.Label(self.exit_frame, text="Which Rule?").grid(row=3, column=2)
        self.rule_which = ttk.Entry(self.exit_frame)
        self.rule_which.grid(row=3, column=3)
        
        self.btn_close = ttk.Button(self.exit_frame, text="CLOSE TRADE", command=self.close_trade, state="disabled")
        self.btn_close.grid(row=4, column=0, columnspan=4, pady=20)

    def refresh_open_trades(self):
        # Clear tree
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        df = data_manager.get_open_trades()
        if not df.empty:
            for _, row in df.iterrows():
                self.tree.insert("", "end", values=(
                    row['Trade_ID'], row['Entry_Date'], row['Symbol'], 
                    row['Strategy'], row['Lots'], row['Spread_Entry_Price']
                ))

    def on_trade_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        item = self.tree.item(selected_item)
        trade_id = int(item['values'][0])
        self.selected_trade_id = trade_id
        
        # Get full trade details to know strategy
        df = data_manager.load_db()
        trade_row = df[df['Trade_ID'] == trade_id].iloc[0]
        strategy = trade_row['Strategy']
        
        # Setup exit leg fields
        for w in self.exit_legs_frame.winfo_children():
            w.destroy()
        self.exit_leg_widgets = {}
        
        if strategy == "Credit Spread":
            labels = ["Short Leg Exit", "Long Leg Exit"]
            keys = ["Short_Leg_Exit", "Long_Leg_Exit"]
        elif strategy == "Iron Condor":
            labels = ["Short Call Exit", "Long Call Exit", "Short Put Exit", "Long Put Exit"]
            keys = ["Short_Call_Exit", "Long_Call_Exit", "Short_Put_Exit", "Long_Put_Exit"]
        else:
            labels = []
            keys = []
            
        for i, (label, key) in enumerate(zip(labels, keys)):
            ttk.Label(self.exit_legs_frame, text=label).grid(row=0, column=i)
            e = ttk.Entry(self.exit_legs_frame)
            e.grid(row=1, column=i, padx=5)
            self.exit_leg_widgets[key] = e
            
        self.btn_close.config(state="normal")

    def close_trade(self):
        if not hasattr(self, 'selected_trade_id'):
            return

        try:
            # Gather Exit Data
            exit_data = {
                "Exit_Date": self.exit_date.get(),
                "Spread_Exit_Price": float(self.exit_price.get()),
                "Adjustment_Made": self.adj.get(),
                "Exit_Emotion": self.emo.get(),
                "Rule_Broken": self.rule.get(),
                "Rule_Broken_Which": self.rule_which.get()
            }
            
            for key, widget in self.exit_leg_widgets.items():
                val = widget.get()
                exit_data[key] = float(val) if val else 0.0
                
            # Perform Calculations
            df = data_manager.load_db()
            trade_row = df[df['Trade_ID'] == self.selected_trade_id].iloc[0]
            
            computed = analytics.calculate_trade_metrics(trade_row, exit_data)
            
            # Save
            data_manager.update_trade_to_closed(self.selected_trade_id, exit_data, computed)
            
            messagebox.showinfo("Success", "Trade Closed Successfully")
            self.refresh_open_trades()
            self.btn_close.config(state="disabled")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid Input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"System Error: {e}")

    def setup_analytics_tab(self):
        self.stats_text = tk.Text(self.tab_analytics, height=20, width=80)
        self.stats_text.pack(pady=20, padx=20)
        
    def refresh_analytics(self):
        df_closed = data_manager.get_closed_trades()
        metrics = analytics.calculate_portfolio_metrics(df_closed)
        
        text = f"PORTFOLIO ANALYTICS\n{'='*30}\n\n"
        text += f"Total Closed Trades: {metrics['Total_Trades']}\n"
        text += f"Cumulative PnL:      ${metrics['Cumulative_PnL']:.2f}\n"
        text += f"Win Rate:            {metrics['Win_Rate']:.2f}%\n"
        text += f"Expectancy:          ${metrics['Expectancy']:.2f}\n"
        text += f"Max Drawdown:        ${metrics['Max_Drawdown']:.2f}\n"
        text += f"Current Drawdown:    ${metrics['Drawdown']:.2f}\n\n"
        
        text += "Equity Curve (Last 10 trades):\n"
        if metrics.get('Equity_Curve'):
            curve = metrics['Equity_Curve'][-10:]
            for val in curve:
                text += f" -> ${val:.2f}\n"
        else:
            text += " No data.\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, text)

if __name__ == "__main__":
    data_manager.initialize_db()
    root = tk.Tk()
    app = TradeJournalGUI(root)
    root.mainloop()
