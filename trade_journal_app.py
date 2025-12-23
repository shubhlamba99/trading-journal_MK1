import tkinter as tk
from gui import TradeJournalGUI
import data_manager

def main():
    data_manager.initialize_db()
    root = tk.Tk()
    app = TradeJournalGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
