from typing import Any, Dict, Optional
import ccxt
from playwright.sync_api import sync_playwright, Route
from undetected_playwright import Tarnished
from fake_useragent import UserAgent
from enum import IntEnum
from loguru import logger
import time
import asyncio
import json

# Actions (buy, sell)
class Actions(IntEnum):
    BUY = 1
    SELL = 2

class BingX:
    def __init__(self,
        api_key: str,
        secret: str,
        fiat: str,
        action: Actions,
        price: float,
        bank: Optional[str] = ""
    ) -> None:
        '''
        Args:
            api_key (str): Token for official API
            secret (str): Secret for official API
            fiat (str): Fiat symbol, like 'RUB'
            action (Actions): Actions.BUY for buying, Actions.SELL for selling
            price (float): The amount of fiat desirebale for selling/buying coin
            bank (Optional[str]): Bank's id
        '''
        self.api_key = api_key
        self.secret = secret
        self.coin = "USDT"
        self.fiat = fiat
        self.action = str(action)
        self.price = price
        self.bank = bank
        # Init official API
        self.api = ccxt.bingx({'apiKey': self.api_key, 'secret': self.secret})
        # Logger
        self.logger = logger
        self.logger.add(f"logs/bingx_{time.strftime('%H%M%S')}.log", format="[ {time} ] [ {level} ] [ {message} ]", rotation="50 MB")

    def setup_playwright(self) -> None:
        '''
        Creating playwright instance
        '''
        try:
            self.playwright = sync_playwright().start()
    
            self.browser = self.playwright.chromium.launch(
                    args = ["--headless=new", "--dump-dom"]
            )
            self.context = self.browser.new_context(
                    locale="ru-RU",
                    user_agent=UserAgent(os="windows", browsers=["chrome"]).random)
            Tarnished.apply_stealth(self.context)
            self.logger.success("Playwirght has been started")
        except Exception as e:
            err_msg = f"Failed to start playwright: {e}"
            self.logger.error(err_msg)
            raise ValueError(err_msg)

    def stop(self) -> None:
        '''
        Properly stops the app
        '''
        #self.api.stop()
        self.browser.close()
        self.playwright.stop()
        self.logger.success("Playwright has been stoped")
        
    def get_banks_and_merchants(self) -> Dict[str, Any]:
        '''
        Used to retrive the list of suitable merchants and banks
        '''
        try:
            url = f"https://bingx.paycat.com/ru-ru/trade/self-selection?fiat={self.fiat}&type={self.action}"
            # Banks handler
            def banks_handler(route: Route) -> None:
                response = route.fetch()
                # Saving to 'raw_banks'
                data = response.json()
                if "data" not in data.keys():
                    err_msg = "Can not retrive banks"
                    self.logger.error(err_msg)
                    raise ValueError(err_msg)
                self.raw_banks = data['data']['paymentMethodList'] 
                del data
                route.fulfill(response=response)
            # Merchants handler
            def merchants_handler(route: Route) -> None:
                # NOTE: Tried to modify requests, but always got error with code 100005 
                # Saving to 'raw_merchants'
                response = route.fetch()
                data = response.json()
                if "data" not in data.keys():
                    err_msg = "Can not retrive banks"
                    self.logger.error(err_msg)
                    raise ValueError(err_msg)
                self.raw_merchants = data['data']['dataList'][:10] # type: ignore
                del data
                route.fulfill(response=response)
            # Setting up handlers
            page = self.context.new_page()
            page.route("https://api-app.qq-os.com/api/c2c/v1/advert/payment/list*", banks_handler)
            page.route("https://api-app.qq-os.com/api/c2c/v1/advert/list*", merchants_handler)
            page.goto(url=url, wait_until="networkidle", timeout = 10000)
            page.close()
            # Prepairing information
            def format_bank(bank: Dict[str, Any]) -> Dict[str, Any]:
                return {
                        "id": bank["id"],
                        "name": bank["name"]
                        }

            def format_merchant(merchant: Dict[str, Any]) -> Dict[str, Any]:
                return {
                        "price": merchant["price"],
                        "merchant": merchant["nickName"],
                        "max": merchant["maxAmount"],
                        "min": merchant["minAmount"],
                        "banks": [bank["id"] for bank in merchant["paymentMethodList"]]
                        }
        except Exception as e:
            err_msg = f"Failed to get banks and merchants: {e}"
            self.logger.error(err_msg)
            raise ValueError(err_msg)

        return {"banks": list(map(format_bank, self.raw_banks)), "merchants": list(map(format_merchant, self.raw_merchants))} # type: ignore

    def get_spot(self) -> Dict[str, Any]:
        '''
        Used to retrive spot info
        '''
        try:
            symbols = ["BTC/USDT", "ETH/USDT", "XAI/USDT",
                       "SOL/USDT", "DOP/USDT", "FTN/USDT",
                       "FDUSD/USDT", "XRP/USDT", "PEPE/USDT",
                       "MNT/USDT", "USDC/USDT", "DOGE/USDT"]
            ctx = self.api.fetch_tickers(symbols)
            
            def format_symbol(symbol: str, data: Any) -> Dict[str, Any]:
                return {'symbol': symbol, 'price': data['close']}

            #pprint(ctx)
            return {'spot': [format_symbol(symbol, data) for symbol, data in ctx.items()]}
        except Exception as e:
            err_msg = f"Failed to get spot info: {e}"
            self.logger.error(err_msg)
            raise ValueError(err_msg)

    def report(self) -> Dict[str, Any]:
        banks_and_merchants = self.get_banks_and_merchants()
        spot = self.get_spot()
        return {
                "banks": banks_and_merchants["banks"],
                "merchants": banks_and_merchants["merchants"],
                "spot": spot["spot"]
                }


def main():
    # NOTE: Only USDT is supported, filters are not applied,
    # symbols in spot are set in code - for all these f@ck ups thanks to CloudFlare 
    # Left api_key and secret empty - it just works somehow 0_0
    bingx = BingX(
        api_key= "",
        secret = "",
        fiat = "RUB",
        action = Actions.SELL,
        price = 115
    )
    bingx.setup_playwright()
    data = bingx.report()
    with open("report.json", "w") as report:
        report.write(json.dumps(data, indent=4))
    bingx.stop()

if __name__ == "__main__":
    main()
