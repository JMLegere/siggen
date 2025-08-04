from __future__ import annotations


from nautilus_trader.backtest.node import (
    BacktestDataConfig,
    BacktestEngineConfig,
    BacktestNode,
    BacktestRunConfig,
    BacktestVenueConfig,
)
from nautilus_trader.config import ImportableStrategyConfig, LoggingConfig
from nautilus_trader.core.message import Event
from nautilus_trader.indicators.macd import MovingAverageConvergenceDivergence
from nautilus_trader.model import InstrumentId, Position, Quantity, QuoteTick, Venue
from nautilus_trader.model.enums import OrderSide, PositionSide, PriceType
from nautilus_trader.model.events import PositionOpened
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.trading.strategy import Strategy, StrategyConfig


class MACDConfig(StrategyConfig):
    """Configuration for the MACD strategy."""

    instrument_id: InstrumentId
    fast_period: int = 12
    slow_period: int = 26
    trade_size: int = 1_000_000
    entry_threshold: float = 0.0001


class MACDStrategy(Strategy):
    """Simple MACD cross-over strategy."""

    def __init__(self, config: MACDConfig) -> None:
        super().__init__(config=config)
        self.macd = MovingAverageConvergenceDivergence(
            fast_period=config.fast_period,
            slow_period=config.slow_period,
            price_type=PriceType.MID,
        )
        self.trade_size = Quantity.from_int(config.trade_size)
        self.position: Position | None = None

    def on_start(self) -> None:
        self.subscribe_quote_ticks(instrument_id=self.config.instrument_id)

    def on_stop(self) -> None:
        self.close_all_positions(self.config.instrument_id)
        self.unsubscribe_quote_ticks(instrument_id=self.config.instrument_id)

    def on_quote_tick(self, tick: QuoteTick) -> None:
        self.macd.handle_quote_tick(tick)
        if not self.macd.initialized:
            return
        self.check_for_entry()
        self.check_for_exit()

    def on_event(self, event: Event) -> None:
        if isinstance(event, PositionOpened):
            self.position = self.cache.position(event.position_id)

    def open_position(self, side: OrderSide) -> None:
        order = self.order_factory.market(
            instrument_id=self.config.instrument_id,
            order_side=side,
            quantity=self.trade_size,
        )
        self.submit_order(order)

    def check_for_entry(self) -> None:
        value = self.macd.value
        threshold = self.config.entry_threshold

        if value > threshold and (
            not self.position or self.position.side != PositionSide.LONG
        ):
            self.open_position(OrderSide.BUY)
        elif value < -threshold and (
            not self.position or self.position.side != PositionSide.SHORT
        ):
            self.open_position(OrderSide.SELL)

    def check_for_exit(self) -> None:
        if not self.position:
            return

        if self.macd.value >= 0.0 and self.position.side == PositionSide.SHORT:
            self.close_position(self.position)
        elif self.macd.value < 0.0 and self.position.side == PositionSide.LONG:
            self.close_position(self.position)


def run_backtest() -> None:
    """Run the MACD backtest from the Nautilus Trader quickstart."""
    catalog = ParquetDataCatalog.from_env()
    instruments = catalog.instruments()

    venue = BacktestVenueConfig(
        name="SIM",
        oms_type="NETTING",
        account_type="MARGIN",
        base_currency="USD",
        starting_balances=["1_000_000 USD"],
    )

    data = BacktestDataConfig(
        catalog_path=str(catalog.path),
        data_cls=QuoteTick,
        instrument_id=instruments[0].id,
        end_time="2020-01-10",
    )

    engine = BacktestEngineConfig(
        strategies=[
            ImportableStrategyConfig(
                strategy_path="__main__:MACDStrategy",
                config_path="__main__:MACDConfig",
                config={
                    "instrument_id": instruments[0].id,
                    "fast_period": 12,
                    "slow_period": 26,
                },
            )
        ],
        logging=LoggingConfig(log_level="ERROR"),
    )

    config = BacktestRunConfig(
        engine=engine,
        venues=[venue],
        data=[data],
    )

    node = BacktestNode(configs=[config])
    results = node.run()
    engine_instance = node.get_engine(config.id)
    engine_instance.trader.generate_order_fills_report()
    engine_instance.trader.generate_positions_report()
    engine_instance.trader.generate_account_report(Venue("SIM"))
    return results


if __name__ == "__main__":
    run_backtest()
