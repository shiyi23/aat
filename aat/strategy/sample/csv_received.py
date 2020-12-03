import os
import os.path
from aat import Strategy, Event, Order, Side
from pprint import pprint


class ReceivedStrategy(Strategy):
    def __init__(self, *args, **kwargs) -> None:
        super(ReceivedStrategy, self).__init__(*args, **kwargs)
        self._trade = True
        self._received_count = 0

    async def onStart(self, event: Event) -> None:
        pprint(self.instruments())
        pprint(self.positions())

        for i in self.instruments():
            await self.subscribe(i)

    async def onTrade(self, event: Event) -> None:
        pprint(event)
        if self._trade and event.target.my_order is None:
            await self.newOrder(Order(
                1,
                event.target.price,
                Side.BUY,
                event.target.instrument,
                event.target.exchange,
            ))
            self._trade = False

    async def onReceived(self, event):
        pprint(event)
        self._trade = True
        self._received_count += 1

    async def onExit(self, event: Event) -> None:
        print("Finishing...")


if __name__ == "__main__":
    from aat import TradingEngine, parseConfig

    cfg = parseConfig(
        [
            "--trading_type",
            "backtest",
            "--load_accounts",
            "--exchanges",
            "aat.exchange.generic:CSV,{}".format(
                os.path.join(os.path.dirname(__file__), "data", "aapl.csv")
            ),
            "--strategies",
            "aat.strategy.sample.csv_received:ReceivedStrategy",
        ]
    )
    print(cfg)
    t = TradingEngine(**cfg)
    t.start()
    assert t.strategies[0]._received_count == 64
    
