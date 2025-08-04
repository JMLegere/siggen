# Nautilus Trader Quickstart

This project demonstrates how to run the [Nautilus Trader](https://nautilustrader.io/) quickstart example using Python and Jupyter notebooks. It also installs the [SnapTrade](https://snaptrade.com/) SDK for live execution.

## Setup

1. Install Python 3.11 or later.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Download sample FX data using the script provided by Nautilus Trader:
   ```bash
   curl https://raw.githubusercontent.com/nautechsystems/nautilus_data/main/nautilus_data/hist_data_to_catalog.py | python -
   ```
4. Launch Jupyter to explore the quickstart notebook:
   ```bash
   jupyter notebook
   ```
5. Alternatively run the script directly:
   ```bash
   python quickstart.py
   ```

## Tests

Run the automated tests with:

```bash
pytest
```
