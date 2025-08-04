import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from nautilus_trader.model.objects import Quantity
from quickstart import MACDConfig, MACDStrategy


def test_macd_config_defaults():
    config = MACDConfig(instrument_id="EURUSD")
    assert config.fast_period == 12
    assert config.slow_period == 26
    assert config.trade_size == 1_000_000
    assert config.entry_threshold == 0.0001


def test_strategy_initialization():
    config = MACDConfig(instrument_id="EURUSD")
    strat = MACDStrategy(config)
    assert isinstance(strat.macd, object)
    assert isinstance(strat.trade_size, Quantity)
