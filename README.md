# Options Trade Journal App

A desktop Python application for tracking options trades (Credit Spreads and Iron Condors) with a strict two-phase workflow (Open/Close) and automated analytics.

## Features

- **GUI Interface:** Built with Tkinter.
- **Data Storage:** Excel (`trade_journal.xlsx`) as the single source of truth.
- **Strategies:** Supports Credit Spreads and Iron Condors.
- **Analytics:** Calculates PnL, Win Rate, Expectancy, Drawdown, and Equity Curve.
- **Workflow:** Enforces separation between Entry (Open) and Exit (Close) phases.

## Installation

1. **Prerequisites:** Python 3.10+
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running from Source

To run the application directly with Python:

```bash
python trade_journal_app.py
```

### Building the Executable

To package the application as a single standalone executable:

```bash
pyinstaller trade_journal_app.spec
```

The executable will be generated in the `dist/` directory.

## File Structure

- `trade_journal_app.py`: Main entry point.
- `gui.py`: Graphical User Interface logic.
- `data_manager.py`: Handles Excel database operations.
- `analytics.py`: Financial calculations and metrics.
- `trade_journal.xlsx`: The database (auto-created on first run).
