Python 3.9.13 (tags/v3.9.13:6de2ca5, May 17 2022, 16:36:42) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> prices = Data.get_price_series("Market_Making_Prices", True)
requests = Data.get_price_requests("Market_Making_Requests")

requests_with_prices = []
for request in requests:
    matched_price = prices.loc[request[1], request[0]]
    requests_with_prices.append((request, matched_price))


class QuotedTrade:
    """A class to represent a Quote order"""
    def __init__(self, ticker, trade_volume, ref_price, bid_price, offer_price, date):
        self.ticker = ticker
        self.trade_volume = trade_volume
        self.ref_price = ref_price
        self.bid_price = bid_price
        self.offer_price = offer_price
        self.date = date

    def __str__(self):
        return (f"Trade Request for {self.ticker}, {self.trade_volume} shares "
                f"@ {self.ref_price} on {self.date}. "
                f"Bid Price: {self.bid_price} and Offer Price: {self.offer_price}")

    def __repr__(self):
        return (f"QuotedTrade(ticker={self.ticker}, trade_volume={self.trade_volume}, "
                f"ref_price={self.ref_price}, bid_price={self.bid_price}, "
                f"offer_price={self.offer_price}, date={self.date})")

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


quoted_trades = []
for matched in requests_with_prices:
    delta = 0.02
    bid_price = matched[1] * (1 - delta)
    offer_price = matched[1] * (1 + delta)
    quote = QuotedTrade(
        matched[0][0],
        matched[0][2],
        matched[1],
        bid_price,
        offer_price,
        matched[0][1],
    )
    quoted_trades.append(quote)


mm = MarketMaker.mm(stocks=prices.columns.values)
for quote in quoted_trades:
    mm.add_quoted_trade(quote)  # FIX 1: pass instance, not class


responses = []
for quote in quoted_trades:
    response = HedgeFund.show(quote)  # FIX 2: corrected indentation
    responses.append(response)


class CompletedTrade:  # FIX 3: moved out of for loop to top level
    """A class to represent a Completed trade"""
    def __init__(self, ticker, trade_volume, trade_price, mm_action,
                 ref_price, bid_price, offer_price, date):
        self.ticker = ticker
        self.trade_volume = trade_volume
        self.trade_price = trade_price
        self.mm_action = mm_action
        self.ref_price = ref_price
        self.bid_price = bid_price
        self.offer_price = offer_price
        self.date = date

    def __str__(self):
        return (f"Completed Trade: {self.mm_action} {self.trade_volume} "
                f"{self.ticker} @ {self.trade_price} on {self.date}")

    def __repr__(self):
        return (f"CompletedTrade(ticker={self.ticker}, trade_volume={self.trade_volume}, "
                f"trade_price={self.trade_price}, mm_action={self.mm_action}, "
                f"ref_price={self.ref_price}, bid_price={self.bid_price}, "
                f"offer_price={self.offer_price}, date={self.date})")

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


for response in responses:
    if response.hf_action == "buy":
        trade = CompletedTrade(
            response.ticker,
            response.trade_volume,
            response.offer_price,
            "sell",
            response.ref_price,
            response.bid_price,
            response.offer_price,
            response.date
        )
        mm.add_trade(trade)
    elif response.hf_action == "sell":
        trade = CompletedTrade(
            response.ticker,
            response.trade_volume,
            response.bid_price,
            "buy",
            response.ref_price,
            response.bid_price,
            response.offer_price,
            response.date
        )
        mm.add_trade(trade)
    elif response.hf_action == "refuse":  # FIX 4: handle refused trades
        pass