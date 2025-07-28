from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
import talipp.indicators as ti
from datetime import datetime
import sys

ALPACA_API_KEY = "CantTellYou"
ALPACA_SECRET_KEY = "CantTellYou"

wss_client = StockDataStream(ALPACA_API_KEY, ALPACA_SECRET_KEY)
trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)

# Constants for MACD
short_period = 12
long_period = 26
signal_period = 9

SYMBOL = "SPY"

# client = CryptoHistoricalDataClient()
client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

# Define an empty list to store historical closing prices

buy_signal = False
sell_signal = False
we_are_holding = False

first_transaction = True
we_are_selling = False
we_are_buying = False

buying_amount = 100


def buy(buying_count):
    market_order_data = MarketOrderRequest(
        symbol=SYMBOL,
        qty=buying_count,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )
    # Market order
    trading_client.submit_order(
        order_data=market_order_data
    )


def sell(selling_count):
    market_order_data = MarketOrderRequest(
        symbol=SYMBOL,
        qty=selling_count,  # qty=trading_client.get_all_positions()[0].qty
        side=OrderSide.SELL,
        time_in_force=TimeInForce.DAY
    )
    # Market order
    trading_client.submit_order(
        order_data=market_order_data
    )


macd_indicator = ti.MACD(short_period, long_period, signal_period)


# Create an instance of the MACD indicator
async def bar_data_handler(bars):
    global macd_indicator
    print(bars)

    if datetime.utcnow().hour == 19 and datetime.utcnow().minute >= 40:
        trading_client.close_all_positions(True)
        print("SYSTEM EXITING")
        sys.exit()

    macd_indicator.add_input_value(bars.close)
    print(macd_indicator)
    if len(macd_indicator) < 2:
        return
    last_macd = macd_indicator[-1]

    print("macd=", last_macd.macd, "signal=", last_macd.signal)

    global first_transaction, we_are_selling, we_are_buying, we_are_holding
    # buy/sell every time signal changes

    if last_macd.macd > last_macd.signal and we_are_holding is False:
        we_are_holding = True
        buy(buying_amount)
        print("BUYING ", buying_amount)
    elif last_macd.macd < last_macd.signal and we_are_holding is True:
        we_are_holding = False
        sell(buying_amount)
        print("SELLING", buying_amount)


wss_client.subscribe_bars(bar_data_handler, SYMBOL)
wss_client.run()
