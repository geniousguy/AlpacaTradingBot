# from alpaca.data.live import CryptoDataStream

# from alpaca.data.requests import CryptoBarsRequest
# from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.historical import StockHistoricalDataClient
# from alpaca.data.requests import StockBarsRequest
from alpaca.data.live import StockDataStream
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
import talipp.indicators as ti
import vectorbt as vbt
# from datetime import datetime, timedelta
# from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

ALPACA_API_KEY = "CantTellYou"
ALPACA_SECRET_KEY = "CantTellYou"

wss_client = StockDataStream(ALPACA_API_KEY, ALPACA_SECRET_KEY)
trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)

# Constants for MACD
short_period = 12
long_period = 26
signal_period = 9

SYMBOL = "SPY"

manager = vbt.ScheduleManager()

# client = CryptoHistoricalDataClient()
client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)
# Define an empty list to store historical closing prices

buy_signal = False
sell_signal = False
we_are_holding = False

first_transaction = True
we_are_selling = False
we_are_buying = False

buying_amount = 50


# quantity = trading_client.get_all_positions()[0].qty
# print(quantity)


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

    macd_indicator.add_input_value(bars.close)
    print(macd_indicator)
    if len(macd_indicator) < 2:
        return
    last_macd = macd_indicator[-1]

    print("macd=", last_macd.macd, "signal=", last_macd.signal)

    global first_transaction, we_are_selling, we_are_buying, we_are_holding
    # buy/sell every time signal changes

    if last_macd.macd > last_macd.signal and we_are_buying is False:
        we_are_selling = False
        we_are_buying = True
        if first_transaction is False:
            # preparing market order
            buy(buying_amount * 2)
            print("BUYING 2x")
        else:
            buy(buying_amount)
            print("BUYING 1x")
            first_transaction = False
    elif last_macd.macd < last_macd.signal and we_are_selling is False:
        we_are_selling = True
        we_are_buying = False
        if first_transaction is False:
            sell(buying_amount * 2)
            print("SELLING 2x")
        else:
            sell(buying_amount)
            print("SELLING 1x")
            first_transaction = False


'''
    if last_macd.macd > last_macd.signal and we_are_holding is False:
        we_are_holding = True
        buy(buying_amount)
        print("BUYING 1x")
    elif last_macd.macd < last_macd.signal and we_are_holding is True:
        we_are_holding = False
        sell()
        print("SELLING 1x")
'''

# manager.every(1, "minute").do(bar_data_handler)

# manager.start()


wss_client.subscribe_bars(bar_data_handler, SYMBOL)
wss_client.run()

# Subscribe to quote data
# wss_client.subscribe_bars(bar_data_handler, SYMBOL)

# Run the data stream
# wss_client.run()
